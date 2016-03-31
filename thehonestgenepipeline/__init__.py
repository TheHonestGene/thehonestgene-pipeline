from os import environ
# pass through environment
BASE_FOLDER=environ.get('BASE_FOLDER','./')
GENOTYPE_FOLDER=environ.get('GENOTYPE_FOLDER','/%s/GENOTYPES' % BASE_FOLDER)
DATA_FOLDER=environ.get('DATA_FOLDER','/%s/DATA' % BASE_FOLDER)