import json
import sys
import warnings
from typing import Union, Hashable, Type
import pandas as pd
import pandera
import pandera as pa
import numpy as np
import os
import time
import requests
import datetime
from zipfile import ZipFile
from dateutil.relativedelta import relativedelta
from typing import List,Dict, Any, Tuple
from pydantic import BaseModel, ValidationError


class Functions:

    """
    Functions in this class are:
    - applymap: ....
    - catch_error: ...
    - scheduler_error_handling: ...
    - convert_empty_columns_type: ...
    - dfdate_to_datetime: ...
    - send_error_to_slack: ...
    - gen_dict_extract: ...
    - detect_changes_between_dataframes: ...
    - generate_mutation_list_from_dataframes: ...
    - archive_old_files: ...
    - df_to_xlsx: ...
    - zip_files: ...
    - intervalmatch_dates: ...
    """

    @staticmethod
    def applymap(key: pd.Series, mapping: dict, default=None):
        """
        This function maps a given column of a dataframe to new values, according to specified mapping.
        Column types float and int are converted to object because those types can't be compared and changed
        ----------
        :param key: input on which you want to apply the rename.
        :param mapping: mapping dict in which to lookup the mapping
        :param default: fallback if mapping value is not in mapping dict (only for non Series). If this is not specified, returns the key
        :return: df with renamed columns
        """
        # Use custom dictionary
        if default is None:
            # create custom dictionary that returns key when __missing__ is called
            class SmartDict(dict):
                def __missing__(self, key):
                    return key

            return key.map(SmartDict(mapping))
        else:
            # return default value if a key is missing
            from collections import defaultdict

            return key.map(defaultdict(lambda: default, mapping))

    @staticmethod
    def catch_error(e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error = str(e)[:400].replace('\'', '').replace('\"', '') + ' | Line: {}'.format(exc_tb.tb_lineno)
        raise Exception(error)

    @staticmethod
    def scheduler_error_handling(e: Exception, task_id, run_id, mysql_con, breaking=True, started_at=None):
        """
        This function handles errors that occur in the scheduler. Logs the traceback, updates run statuses and notifies users
        :param e: the Exception that is to be handled
        :param task_id: The scheduler task id
        :param mysql_con: The connection which is used to update the scheduler task status
        :param logger: The logger that is used to write the logging status to
        :param breaking: Determines if the error is breaking or code will continue
        :param started_at: Give the time the task is started
        :return: nothing
        """
        # Format error to a somewhat readable format
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error = str(e)[:400].replace('\'', '').replace('\"', '') + ' | Line: {}'.format(exc_tb.tb_lineno)
        # Get scheduler task details for logging
        task_details = mysql_con.select('task_scheduler', 'queue_name, runfile_path', 'WHERE id = {}'.format(task_id))[0]
        taskname = task_details[0]
        customer = task_details[1].split('/')[-1].split('.')[0]

        if breaking:
            # Set scheduler status to failed
            mysql_con.update('task_scheduler', ['status', 'last_error_message'], ['IDLE', 'Failed'], 'WHERE `id` = {}'.format(task_id))
            # Log to database
            mysql_con.raw_query("INSERT INTO `task_execution_log` VALUES ({}, {}, 'CRITICAL', '{}', {}, '{}')".format(run_id, task_id, datetime.datetime.now(), exc_tb.tb_lineno, error), insert=True)
            mysql_con.raw_query("INSERT INTO `task_scheduler_log` VALUES ({}, {}, 'Failed', '{}', '{}')".format(run_id, task_id, started_at, datetime.datetime.now()),
                insert=True)
            # Notify users on Slack
            Functions.send_error_to_slack(customer, taskname, 'failed')
            raise Exception(error)
        else:
            mysql_con.raw_query("INSERT INTO `task_execution_log` VALUES ({}, {}, 'CRITICAL', '{}', {}, '{}')".format(run_id, task_id, datetime.datetime.now(), exc_tb.tb_lineno, error), insert=True)
            Functions.send_error_to_slack(customer, taskname, 'contains an error')

    @staticmethod
    def convert_empty_columns_type(df: pd.DataFrame):
        """
        Converts the type of columns which are complete empty (not even one value filled) to object. This columns are
        sometimes int or float but that's difficult to work with. Therefore, change always to object
        :param df: input dataframe which must be converted
        :return: dataframe with new column types
        """
        for column in df:
            if df[column].isnull().all():
                df[column] = None

        return df

    @staticmethod
    def dfdate_to_datetime(df: pd.DataFrame, dateformat=None):
        """
        This function processes input dataset and tries to convert all columns to datetime. If this throws an error, it skips the column
        ----------
        :param df: input dataframe for which you want to convert datetime columns
        :param dateformat: optionally specify output format for datetimes. If empty, defaults to %y-%m-%d %h:%m:%s
        :return: returns input df but all date columns formatted according to datetime format specified
        """
        df = df.apply(lambda col: pd.to_datetime(col, errors='ignore').dt.tz_localize(None) if col.dtypes == object else col, axis=0)
        if format is not None:
            # optional if you want custom date format. Note that this changes column type from date to string
            df = df.apply(lambda col: col.dt.strftime(dateformat) if col.dtypes == 'datetime64[ns]' else col, axis=0)
            df.replace('NaT', '', inplace=True)

        return df


    @staticmethod
    def send_error_to_slack(customer, taskname, message, api_token):
        """
        This function is meant to send scheduler errors to slack
        :param customer: Customername where error occured
        :param taskname: Taskname where error occured
        :return: nothing
        """
        message = requests.get('https://slack.com/api/chat.postMessage',
                               params={'channel': 'C04KBG1T2',
                                       'text': 'The reload task of {taskname} from {customer} {message}. Check the {taskname} log for details'.format(customer=customer,
                                                                                                                                                      taskname=taskname,
                                                                                                                                                      message=message),
                                       'username': 'Task Scheduler',
                                       'token': f'{api_token}'},
                               timeout=600).content

    @staticmethod
    def gen_dict_extract(key, var):
        """
        Looks up a key in a nested dict until its found.
        :param key: Key to look for
        :param var: input dict (don't set a type for this, since it can be list as well when it recursively calls itself)
        :return: Generator object with a list of elements that are found. Acces with next() to get the first value or for loop to get all elements
        """
        if hasattr(var, 'items'):
            for k, v in var.items():
                if k == key:
                    yield v
                if isinstance(v, dict):
                    for result in Functions.gen_dict_extract(key, v):
                        yield result
                elif isinstance(v, list):
                    for d in v:
                        for result in Functions.gen_dict_extract(key, d):
                            yield result

    @staticmethod
    def detect_changes_between_dataframes(df_old: pd.DataFrame, df_actual: pd.DataFrame, check_columns: list, unique_key: str | list, keep_old_values: Union[str, bool] = False, detect_column_changes: bool = False, ignore_new_empty_value_in_column: Union[bool, list] = False):
        """
        This function reads data from today and yesterday, flags this data according to old and new
        ----------
        :param df_old: A dataframe with the old values
        :param df_actual: A dataframe with the actual value. This one will be compared to the old_df
        :param check_columns: list of column(s) which you want to be used to check for changes in data
        :param unique_key: list of column(s) which you want to be used in order to group data. This should be the unique key which is always the same in data of today and yesterday
        :param keep_old_values: a parameter of type boolean (for backwards compatibility) or string. Optional values are: dict, rows, list.
        Dict gives a column which contains a dict of changed fields and corresponding values, list gives changed fields and changed values in two separate columns in a list, rows keeps the old entry in a separate df row (flagged with flag_old).
        :param detect_column_changes: detect new column as change
        :param ignore_new_empty_value_in_column: ignore change if new value is empty. If True, will apply to all columns. If list, will only apply to columns in list. If False, will not ignore empty values.
        Default behaviour is False, returning nothing. If any value is given outside dict,rows,list, will also default to False.
        :return: Returns a dataframe with the new columns change_type (deleted, new or edited) and changed_fields (contains all the names of the changed fields)
        """
        # Set default if parameter outside possible options is given
        if isinstance(unique_key, list):
            # Check if the old dataframe is empty, if so, add a column with the unique key for comparison
            if df_old.empty:
                df_old['combined_unique_key'] = pd.Series(dtype=str)
            else:
                df_old['combined_unique_key'] = df_old[unique_key].astype(str).agg(''.join, axis=1)

            # Check if the actual dataframe is empty, if so, add a column with the unique key for comparison
            if df_actual.empty:
                df_actual['combined_unique_key'] = pd.Series(dtype=str)
            else:
                df_actual['combined_unique_key'] = df_actual[unique_key].astype(str).agg(''.join, axis=1)
            unique_key = 'combined_unique_key'
        if keep_old_values not in ['dict', 'rows', 'list', False]:
            keep_old_values = False
            warnings.warn('Value for keep_old_values was outside list of possible parameters, defaulting to False')
        if isinstance(ignore_new_empty_value_in_column, bool) and ignore_new_empty_value_in_column == True:
            ignore_new_empty_value_in_column = check_columns
        if not df_old[unique_key].is_unique:
            print("Duplicated records:")
            print(df_old[df_old[unique_key].duplicated(keep=False)].to_string())
            raise ValueError('The unique_key column is not unique in the old dataframe')
        if not df_actual[unique_key].is_unique:
            print("Duplicated records:")
            print(df_actual[df_actual[unique_key].duplicated(keep=False)].to_string())
            raise ValueError('The unique_key column is not unique in the actual dataframe')

        if detect_column_changes:
            deleted_columns = [column for column in df_old.columns.values if column not in df_actual.columns.values]
            added_columns = [column for column in df_actual.columns.values if column not in df_old.columns.values]
            df_old[added_columns] = [pd.NA] * len(added_columns)
            # set values of columns to object because one of the dataframes only contains NA values
            df_old = df_old.astype(dtype={key: 'object' for key in added_columns})
            df_actual = df_actual.astype(dtype={key: 'object' for key in added_columns})
            df_actual[deleted_columns] = [pd.NA] * len(deleted_columns)
            df_actual = df_actual.astype(dtype={key: 'object' for key in deleted_columns})
            df_old = df_old.astype(dtype={key: 'object' for key in deleted_columns})

        # Checking if the types of the columns (both check_columns and unique_key) correspond between df_old and df_new and raising an error if not
        for column in check_columns + [unique_key]:
            # int64 and float64 are an exception: a combination of these two types works fine
            if not (df_old[column].dtype in ['int64', 'float64'] and df_actual[column].dtype in ['int64', 'float64']) \
                    and not df_old[column].dtype == df_actual[column].dtype:
                raise ValueError(f'The types of the column \'{column}\' do not correspond between df_old ('
                                 f'{df_old[column].dtype}) and df_actual ({df_actual[column].dtype}).')
        df_old['flag_old'] = 1
        df_actual['flag_old'] = 0

        # Removed sort parameter from concat because this sort columns alphabetically (for no reason)
        df = pd.concat([df_old, df_actual]).drop_duplicates(subset=check_columns + [unique_key], keep=False)
        df['freq'] = df.groupby(unique_key, observed=True)[unique_key].transform('count')  # observed parameter is for Categorical data (it will check if the possible values for a column are the same as another column). But you only want to compare the actually present value
        df['change_type'] = np.where(np.logical_and(df.freq == 1, df.flag_old == 0), 'new',
                                     np.where(np.logical_and(df.freq == 1, df.flag_old == 1), 'deleted',
                                              np.where(df.freq == 2, 'edited',
                                                       'duplicates in data'
                                                       )
                                              )
                                     )
        # Now check which values in which column are changed. Add the names of this columns to the column 'changed_fields'
        df.sort_values(by=[unique_key] + ['flag_old'], inplace=True, ascending=False)
        df.reset_index(inplace=True, drop=True)
        df['changed_fields'] = ''
        # If the unique key is already in the columns which need to be checked, then don't add this double. Otherwise comparison of rows won't work because two values are returned for an index
        if unique_key in check_columns:
            df_changes = df.loc[:, check_columns]
        else:
            df_changes = df.loc[:, check_columns + [unique_key]]
        for i in df_changes.index.values:
            curr_dict: dict = df_changes.iloc[i].to_dict()
            prev_dict: dict = df_changes.iloc[i - 1].to_dict()
            if curr_dict[unique_key] == prev_dict[unique_key] and i != 0:
                # returns a series with a boolean for the columns which are different
                changed_columns_dict = {key: (curr_dict[key], prev_dict[key]) for key in curr_dict if not (pd.isna(curr_dict[key]) and pd.isna(prev_dict[key])) and curr_dict[key] != prev_dict[key]}
                # Apply the ignore_change_if_new_value_is_empty condition
                if isinstance(ignore_new_empty_value_in_column, list):
                    # Check if the column is specified to ignore changes when new value is empty
                    changed_columns_dict = {key: (value_new, value_old) for key, (value_new, value_old) in changed_columns_dict.items() if key not in ignore_new_empty_value_in_column or not (pd.isna(value_new) or value_new == '')}
                if keep_old_values == 'list':
                    df.loc[i, 'changed_fields'] = str([key for key in changed_columns_dict.keys() if key != 'flag_old'])
                    df.loc[i, 'old_values'] = str([value_old for key, (value_new, value_old) in changed_columns_dict.items() if key != 'flag_old'])
                elif keep_old_values == 'dict':
                    import json
                    df.loc[i, 'changes'] = json.dumps({key: str(value_old) for key, (value_new, value_old) in changed_columns_dict.items() if key != 'flag_old'})
                elif keep_old_values == 'rows' or keep_old_values is False:
                    df.loc[i, 'changed_fields'] = str([key for key in changed_columns_dict.keys() if key != 'flag_old'])

        # remove old rows except for when return type is rows
        if keep_old_values != 'rows':
            df = df[(df['flag_old'] == 0) | (df['change_type'] == 'deleted')]
            df.drop(labels=['flag_old', 'freq'], axis='columns', inplace=True, errors='ignore')
        else:
            df['changed_fields'].fillna('', inplace=True)
            df = df[(df['changed_fields'] != '') & (df['changed_fields'] != '[]') & (df['change_type'] == 'edited') | (df['change_type'] != 'edited')]

        if keep_old_values == 'dict':
            df['changes'] = '' if 'changes' not in df.columns else df['changes']
            df = df[(df['changes'] != '{}') & (df['change_type'] == 'edited') | (df['change_type'] != 'edited')]
            del df['changed_fields']

        if 'combined_unique_key' in df.columns:
            del df['combined_unique_key']

        return df

    @staticmethod
    def save_mutations_and_clean_overdue_mutations(changes_dir: str, df: pd.DataFrame, max_retries: int = None, max_days: int = None) -> pd.DataFrame:
        """
        This method saves your df_changes with any previously saved (failed) changes. This makes sure that you never lose any mutations ever again.
        You have to specify either max_retries or max_days to prevent the mutations from being stuck forever. You can also specify both.
        You should clean up your comparison files right after this method to prevent mutations from being added to this file twice
        :param changes_dir: directory where you want to store the file with mutations
        :param df: dataframe with mutations (mostly this will be the df right before you process it to an external system)
        :param max_retries: amount of times a mutations should be retried after it failed once
        :param max_days: amount of days a mutation should be saved maximally
        :return: dataframe with your new changes and any changes that were present from previous runs
        """
        archive_changes_dir = f"{changes_dir}/archive/"
        os.makedirs(changes_dir, exist_ok=True)
        os.makedirs(archive_changes_dir, exist_ok=True)
        df['sync_mutation_date'] = datetime.datetime.today().date()
        df['sync_tried_count'] = 0
        if 'mutations.parquet' in os.listdir(changes_dir):
            df_old = pd.read_parquet(f"{changes_dir}/mutations.parquet")
            df_archive = pd.read_parquet(f"{archive_changes_dir}/archived_mutations.parquet") if 'archived_mutations.parquet' in os.listdir(archive_changes_dir) else pd.DataFrame()
            df_to_be_archived = pd.DataFrame()
            # cleanup entries that reached max age or retries
            if max_retries is not None:
                # Archive max retries reached
                df_to_be_archived = df_old[df_old['sync_tried_count'] >= max_retries]
                df_old = df_old[df_old['sync_tried_count'] <= max_retries]
            if max_days is not None:
                # Archive max days reached
                df_to_be_archived = df_old[df_old['sync_mutation_date'] >= datetime.datetime.today() - relativedelta(days=max_days)]
                df_old = df_old[df_old['sync_mutation_date'] <= datetime.datetime.today() - relativedelta(days=max_days)]
            df = pd.concat([df_old, df])
            df_to_be_archived['sync_status'] = 'Max retries reached'
            df_archive = pd.concat([df_archive, df_to_be_archived])
            df_archive.to_parquet(f"{archive_changes_dir}/archived_mutations.parquet")
        df.reset_index(inplace=True, drop=True)
        df.to_parquet(f"{changes_dir}/mutations.parquet")
        print("Saved mutation dataframe")

        return df

    @staticmethod
    def handle_mutation_result(changes_dir: str, df: pd.DataFrame, succes: bool = True, row_index: Hashable = None):
        """
        This function processes the result of a mutation synchronization. It removes the mutation from the mutation file in case of success and raises the tried_count in case of a fail.
        You should use this function always inside a loop (for index, row in df.iterrows) that iterates over the df returned by save_mutations_and_clean_overdue_mutations. You can then use the index to drop synced rows from the dataframe
        :param changes_dir: directory where you want to store the file with mutations
        :param df: pass the df that is returned by save_mutations_and_clean_overdue_mutations (the df you are processing) to this function so the synced row can be dropped and saved
        :param row_index: pass the index of the row to be updated
        :param succes: if result of sync is success, pass True, else pass False
        """
        archive_changes_dir = f"{changes_dir}/archive/"
        df_archive = pd.read_parquet(f"{archive_changes_dir}/archived_mutations.parquet") if 'archived_mutations.parquet' in os.listdir(archive_changes_dir) else pd.DataFrame()
        if row_index is None:
            if succes:
                df_archive_entry = df.copy()
                df_archive_entry['sync_status'] = 'Success'
                # empty the dataframe while keeping the column names
                df = df.iloc[0:0]
                df.to_parquet(f"{changes_dir}/mutations.parquet")
                df_archive = pd.concat([df_archive, df_archive_entry])
                df_archive.to_parquet(f"{archive_changes_dir}/archived_mutations.parquet")
            else:
                df['sync_tried_count'] += 1
                df.to_parquet(f"{changes_dir}/mutations.parquet")
        else:
            if succes:
                df_archive_entry = df.loc[[row_index]]
                df_archive_entry['sync_status'] = 'Success'
                df.drop(row_index, inplace=True)
                df.to_parquet(f"{changes_dir}/mutations.parquet")
                df_archive = pd.concat([df_archive, df_archive_entry])
                df_archive.to_parquet(f"{archive_changes_dir}/archived_mutations.parquet")
            else:
                df.loc[row_index, 'sync_tried_count'] += 1
                df.to_parquet(f"{changes_dir}/mutations.parquet")

    @staticmethod
    def complement_columns_from_different_dataframes(df_left: pd.DataFrame, df_right: pd.DataFrame, fields: List[str], on: List[str] | str):
        """
        This method is meant for when you have two dataframes with columns that you want to complement when some values in your left dataframe are NA.
        Example df_left:    | A   B       df_right: | A   B     Result: | A   B
                            | 1   5                 | 1   4             | 1   5
                            | 8   NaN               | 8   6             | 8   6
        Example usecase: Both of the systems you are comparing contain an email address. When your df_new has an empty email address and your df_old has an email address, you do not want to overwrite the value.
                         You will then use the Functions.combine_values_from_columns(df_left=df_new, df_right=df_old, fields=['email_address'], on='employee_id')
                         This updates the value in your df_new to be the same as your df_old (so it won't detect as a change, only when there is a new value in you df_new).
        :param df_left: df with values you want to complement
        :param df_right: df with complementary values
        :param fields: one or more fields you want to complement with values from another dataframe
        :param on: key on which to merge the values
        """
        if isinstance(on, str):
            on = [on]
        for col in on:
            if df_left[col].dtype != df_right[col].dtype:
                raise ValueError(f"Data type mismatch in column '{col}': "
                                 f"{df_left[col].dtype} (df_left) vs {df_right[col].dtype} (df_right)")

        df_left.set_index(on, inplace=True, drop=False)
        for field in fields:
            df_left[field].update(df_right.drop_duplicates(on).set_index(on)[field])
        df_left.reset_index(drop=True, inplace=True)

    @staticmethod
    def generate_mutation_list_from_dataframes(df: pd.DataFrame, check_columns: list, unique_key: str):
        """
        This function compares the current row with the previous row, if the employeenumbers of these rows are the same.
        ----------
        :param df: Provide df which contains only edited data. Mandatory column in this df: employee_id
        :param check_columns: Provide the columns which you want to check for edited data. Only these columns will be checked
        :return: df with only mutations. This df contains four columns: employee, mutation type, old value and new value. For each mutation type, a new row will be created
        """
        df = df.loc[:, check_columns].fillna('')
        df.reset_index(inplace=True, drop=True)
        changes = pd.DataFrame()
        for i in df.index.values:
            curr_row = df.iloc[i]
            prev_row = df.iloc[i - 1]
            if curr_row[unique_key] == prev_row[unique_key] and i != 0:
                changed_columns = curr_row != prev_row
                new_vals = curr_row.loc[changed_columns]
                old_vals = prev_row.loc[changed_columns]
                for key in old_vals.keys():
                    changes = changes.append({'Employee': curr_row[unique_key], 'Mutation type': key, 'Old Value': old_vals[key], 'New Value': new_vals[key]}, ignore_index=True)

        return changes

    @staticmethod
    def archive_old_files(source_path: str, archive_path: str, comparison_data_path=None, archive_file_age_in_days=90):
        """
        This method moves all files from a source to a specified archive and cleans files from this archive that are older than archive_file_age_in_days
        :param source_path: source where to archive files from
        :param archive_path: archive path
        :param archive_file_age_in_days: all archived files older than this amount of days, will be moved
        :param comparison_data_path: optional comparison data path (standard method for detecting changes). This add extra functionality
        :return:
        """
        os.makedirs(source_path, exist_ok=True)
        os.makedirs(archive_path, exist_ok=True)
        os.makedirs(comparison_data_path, exist_ok=True)
        for file in os.listdir(archive_path):
            if os.stat(archive_path + file).st_mtime < time.time() - archive_file_age_in_days * 86400:
                os.remove(archive_path + file)
        # If a comparison data path is specified, this functions moves data from source to comparison, and from comparison to archive
        if comparison_data_path is not None:
            for file in os.listdir(comparison_data_path):
                os.rename(comparison_data_path + file, archive_path + str(datetime.datetime.now()) + file)
            for file in os.listdir(source_path):
                os.rename(source_path + file, comparison_data_path + file)
        else:
            for file in os.listdir(source_path):
                os.rename(source_path + file, archive_path + str(datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')) + file)

    @staticmethod
    def cleanup_previous_store_actual(directory: str, actual_df: pd.DataFrame, remove_archived_files_after_days=31):
        """
        This method creates a file structure with actual, previous and archive folders. In every run, files will be moved between the folders so
        it's possible to compare files from the previous run with the current one
        :param directory: The full directory, including basedir, where the actual, previous and archive files will be stored
        :param actual_df: The new file which will be stored in the actual folder
        :param remove_archived_files_after_days: Give an integer after how many days files should be removed from the archive folder.
        return: the full location of the actual and previous file. Can be used in the compare later
        """
        os.makedirs(f'{directory}/actual/', exist_ok=True)
        os.makedirs(f'{directory}/previous/', exist_ok=True)
        os.makedirs(f'{directory}/archive/', exist_ok=True)
        # Move files which are in the previous folder, to the archive folder.
        for file in os.listdir(f'{directory}/previous/'):
            os.rename(f'{directory}/previous/{file}', f'{directory}/archive/{file}')
        # Move files from the previous run (which are in the actual dir, to the folder with previous files.
        previous_file = None
        for file in os.listdir(f'{directory}/actual/'):
            previous_file = f'{directory}/previous/{file}'
            os.rename(f'{directory}/actual/{file}', f'{directory}/previous/{file}')

        # Remove files in the archive folder if they're older than the given age in days
        for file in os.listdir(f'{directory}/archive/'):
            if os.stat(f'{directory}/archive/{file}').st_mtime < time.time() - remove_archived_files_after_days * 86400:
                os.remove(f'{directory}/archive/{file}')

        # Store the new file in the actual folder if there is a new file given.
        new_file = f'{directory}/actual/{int(time.time())}.parquet'
        actual_df.reset_index(drop=True, inplace=True)
        actual_df.to_parquet(new_file)

        return {'new_file': new_file, 'previous_file': previous_file}

    @staticmethod
    def reverse_cleanup_files(directory: str):
        """
        When a script fails, sometimes the files in the actual and previous folders should be moved back onto the situation
        before the script started to make it possible to compare later again.
        :param directory: The full directory, including basedir, where the actual, previous and archive files are stored
        """
        for file in os.listdir(f'{directory}/actual/'):
            os.rename(f'{directory}/actual/{file}', f'{directory}/archive/ERR-{file}')
        for file in os.listdir(f'{directory}/previous'):
            os.rename(f'{directory}/previous/{file}', f'{directory}/actual/{file}')

    @staticmethod
    def df_to_xslx(filepath: str, df: pd.DataFrame, sheetname: str, columns=None):
        """
        This method exports a dataframe to excel. If no columns are specified, then whole DF is exported. Columns will be the DF columns
        If columns are specified, these will be used as header row. Only DF columns that are in the columns list, will be filled with data, rest is ignored
        :param df: input dataframe with data
        :param sheetname: sheetname to write to
        :param columns: list of columns which are accepted in Excel. DF column name must match one of these to be processed
        :return: void
        """
        writer = pd.ExcelWriter(filepath,
                                engine='xlsxwriter',
                                options={'remove_timezone': True})
        if columns is not None:
            columns = list(columns)
            df_columns = df.columns.values.tolist()

            # Add data to columns
            for df_column in df_columns:
                if df_column in columns:
                    series = df[df_column]
                    print(series.to_excel(writer, sheet_name=sheetname, startcol=columns.index(df_column), index=False, startrow=1, header=False))

            # Add custom headercolumns
            if len(df) > 0:
                worksheet = writer.sheets[sheetname]
                workbook = writer.book
                header_format = workbook.add_format({'bold': True})
                for i in columns:
                    worksheet.write(0, columns.index(i), i, header_format)
        else:
            df.to_excel(writer, sheet_name=sheetname, index=False)

    @staticmethod
    def zip_files(source_folder: str, output_filename: str, keep_original_files=True):
        """
        This method zips all the files in a folder
        :return: nothing
        """
        with ZipFile(output_filename, 'w') as zip:
            for file in os.listdir(source_folder):
                zip.write(source_folder + file, file)
                if not keep_original_files:
                    os.remove(source_folder + file)

    @staticmethod
    def send_message_to_teams(title, message_content, action_name=None, action_url=None, group_id=None, tenant_id=None, webhook_id=None):
        """
        This functions sends an automatically generated message to Teams, formatted and with the colour of BrynQ.
        :param title: title of the error message
        :param message_content: content of the error message
        :param action_name: If a button that is linked to an action is needed, this needs to be filled with the name of this button. Else can be set to None.
        :param action_url: Here the redirect link what the button needs to open has to be filled. If there is no button, this can be set to None.
        :return: returns the status code and the message to see if sending the message to Teams worked.
        """

        group_id = os.getenv("TEAMS_GROUP_ID", group_id)
        tenant_id = os.getenv("TEAMS_TENANT_ID", tenant_id)
        webhook_id = os.getenv("TEAMS_WEBHOOK_ID", webhook_id)
        if group_id is None or tenant_id is None or webhook_id is None:
            raise ValueError("Set TEAMS_GROUP_ID, TEAMS_TENANT_ID, TEAMS_WEBHOOK_ID in your .env or pass the optional function parameters to send a message to Teams")
        url = f'https://salurebv.webhook.office.com/webhookb2/{group_id}@{tenant_id}/IncomingWebhook/{webhook_id}'
        if action_name == None:
            body = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": 'F3910F',
                "summary": "Summary",
                "sections": [{
                    "activityTitle": title,
                    "facts": [{
                        "name": "",
                        "value": message_content
                    }],
                    "markdown": False
                }]
            }
        else:
            body = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": 'F3910F',
                "summary": "Summary",
                "sections": [{
                    "activityTitle": title,
                    "facts": [{
                        "name": "",
                        "value": message_content
                    }],
                    "markdown": False
                }],
                "potentialAction": [{
                    "@type": "OpenUri",
                    "name": action_name,
                    "targets": [{
                        "os": "default",
                        "uri": action_url
                    }]
                }]
            }
        response = requests.post(url, json=body, timeout=600)
        return response, response.status_code, response.text

    @staticmethod
    def send_error_to_teams(database, task_number, task_title):
        """
        This function makes sure that the content that is sent to Teams, using the teams message function, is in a formatted table. This is done using HTML.
        :param database: the name of the database, for example sc_brynq.
        :param task_number: the task id of the task that needs to be reported in Teams.
        :param task_title: the name of the specific task that needs to be reported in Teams.
        :return: returns the response of whether the message has been sent successfully. If so, this message contains a formatted table with the information.
        """
        task = f'<table><col width=220><col width=60><col width=400><thead><th>Database</th><th>ID</th><th>Description</th></thead><tbody><tr><td>{database}</td>' \
               f'<td>{task_number}</td><td>{task_title}</td></tr></tbody></table>'
        response = Functions().send_message_to_teams(title='From Python with love - Failed task in the SC Scheduler', message_content=task, action_name='Open Task Scheduler', action_url='https://app.brynq.com/interfaces/')
        return response

    @staticmethod
    def validate_data(df: pd.DataFrame, schema: Type[pa.DataFrameModel], debug: bool = False) -> (pd.DataFrame, pd.DataFrame):
        # if the df is empty, we initialize an empty df with the columns from the schema so the structure and dtypes are always consistent
        if df.empty:
            df = pd.DataFrame(columns=schema.to_schema().columns.keys())
        if not df.index.is_unique:
            warnings.warn("Index was not unique, resetted it. Otherwise we can't drop the correct rows")
            df.reset_index(inplace=True, drop=True)
        try:
            valid_data = schema.validate(df, lazy=True)
            invalid_data = valid_data.copy()[0:0]
        except pa.errors.SchemaErrors as exc:
            if debug:
                print(json.dumps(exc.message, indent=2))
                print("Schema errors and failure cases:")
                print(exc.failure_cases.to_string())
            invalid_indices = (exc.failure_cases['index'].dropna().unique().tolist())
            valid_data = exc.data.copy()
            valid_data = valid_data.drop(index=invalid_indices)
            invalid_data = df.loc[invalid_indices].copy()
            invalid_data = pd.merge(invalid_data, exc.failure_cases, how='left', left_index=True, right_on='index')
            # validate again so correct dtypes can now be set
            valid_data = schema.validate(valid_data, lazy=True)

        return valid_data, invalid_data

    @staticmethod
    def validate_pydantic_data(
            data: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame],
            schema: Type[BaseModel],
            debug: bool = False
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Validates incoming data (a single dict, a list of dicts, or a Pandas DataFrame)
        against a Pydantic schema. Returns a tuple containing the valid records and
        the invalid records. Invalid records include validation error details.

        Args:
            data: The data to be validated. Can be a single dict, a list of dicts, or a pd.DataFrame.
            schema: The Pydantic model (BaseModel) used for validation.
            debug (bool): If True, prints error details to the console for debugging.

        Returns:
            Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
                - valid_data: A list of records that passed validation.
                - invalid_data: A list of records that failed validation, each containing
                                `_validation_errors` with details about the errors.
        """

        # If data is a single dict, convert it to a list of dicts
        if isinstance(data, dict):
            data = [data]
        # If data is a DataFrame, convert it to a list of dicts
        elif isinstance(data, pd.DataFrame):
            data = data.to_dict(orient="records")

        valid_data = []
        invalid_data = []

        # Now 'data' is guaranteed to be a list of dicts
        for idx, item in enumerate(data):
            try:
                # Validate each item using the Pydantic schema
                validated_item = schema(**item).model_dump()
                valid_data.append(validated_item)
            except ValidationError as e:
                if debug:
                    print(f"Validation error at index {idx}:")
                    print(e.json(indent=2))

                # Add error details to the invalid record
                invalid_item = dict(item)
                invalid_item['_validation_errors'] = [
                    {
                        'loc': ' -> '.join(str(loc) for loc in error['loc']),
                        'msg': error['msg'],
                        'type': error['type']
                    }
                    for error in e.errors()
                ]
                invalid_data.append(invalid_item)

        return valid_data, invalid_data
