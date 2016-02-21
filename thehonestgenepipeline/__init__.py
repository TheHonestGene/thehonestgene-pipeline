from os import environ
# pass through environment
BASE_FOLDER=environ['BASE_FOLDER']
GENOTYPE_FOLDER='/%s/GENOTYPES' % BASE_FOLDER
DATA_FOLDER='/%s/DATA' % BASE_FOLDER