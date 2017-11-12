import datetime

from astropy.io import ascii
from astropy.table import Column


def read_rename(filename, rename_dict=None, date_format=None,
                remove_language=False):
    """Update columns names and their data if they are dates from csv files

    inputs
    ------
    filename : str
      name of the file that we want to modify

    rename_dict : dict
      dictionary with the old and new values as key/values respectively

    date_format : dict
      dictionary with the field names and the format in which they date is in
      the file

    remove_languages : boolean
      whether the language column want to be removed
    """
    data = ascii.read(filename, delimiter=';')
    if rename_dict:
        for k, v in rename_dict.items():
            data[k].name = v
    if date_format:
        for k, v in date_format.items():
            column_i = [datetime.datetime.strptime(x, v) for x in data[k]]
            data.remove_column(k)
            data.add_column(Column(data=column_i, name=k))
    if ('language' in data.keys()) and remove_language:
        data.remove_column('language')
    ascii.write(data, filename, format='csv', delimiter=';', overwrite=True)


# Update dates on lookup_timesfits
filename_fits = 'lookup_timesfits.csv'
rename_dict = {'id_filename': 'id', 'date': 'obs_date'}
date_format = {'obs_date': '%Y-%m-%dT%H:%M:%SZ'}
read_rename(filename_fits, rename_dict, date_format)

# Update classifications
filename_class = 'classifications_noRepeated.csv'
# rename fields
rename_dict = {'id_classification': 'id',
               'classification_id': 'zooniverse_class',
               'created_at': 'date_created', 'id_user': 'user_id',
               'id_image_0': 'image_id_0', 'id_image_1': 'image_id_1',
               'more_complex': 'image0_more_complex_image1',
               'inverted': 'used_inverted', 'lang': 'language',
               'started_at': 'date_started', 'finished_at': 'date_finished'}
date_format = {'date_created':  '%Y-%m-%d %H:%M:%S %Z',
               'date_started': '%a, %d %b %Y %H:%M:%S %Z',
               'date_finished': '%a, %d %b %Y %H:%M:%S %Z'}
read_rename(filename_class, rename_dict, date_format, remove_language=True)


# Update fields of rankings
filename_ranking = 'rankings.csv'
rename_dict = {'id_rank': 'id', 'id_image': 'image_id', 'k': 'k_value'}
read_rename(filename_ranking, rename_dict)

# update fields of users
filename_users = 'lookup_users.csv'
rename_dict = {'id_user': 'id', 'user_name': 'username'}
read_rename(filename_users, rename_dict)

# update fields of images
filename_images = 'lookup_properties.csv'
rename_dict = {'id_image': 'id', 'image': 'filename'}
read_rename(filename_images, rename_dict)
