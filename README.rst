********************
TheHonestGenePipeline
********************

TheHonestGenePipeline provides celery tasks for carrying out imputation, ancestry and risk prediction


How-To
***********

Typical usage is to start a celery worker::

    export CELERY_BROKER='amqp://myhost'
    export BASE_FOLDER='[BASE_FOLDER_THAT_CONTAINS_GENOTYPES_AND_DATA]'
    celery worker --app=thehonestgenepipeline

The BASE_FOLDER must be accessible from the celery workers (i.e. NFS share) and must 
contain following folders and files: 

* DATA 
    * weights.hdf5
    * pcs.hdf5
    * hapmap.hdf5
* GENOTYPES
    * ORIGINAL
        * genotype.hdf5
    * IMPUTED (empty)

To generate the weights.hdf5, pcs.hdf5 and hapmap.hdf5 file refer to the `imputor <https://github.com/TheHonestGene/imputor>`_ and `ancestor <https://github.com/TheHonestGene/ancestor/blob/master/README.rst>`_ libraries.
The ORIGINAL folder must contain the original genotypes in hdf5 format and the IMPUTED folder will contain the imputed genotypes.

There are 3 steps to run an entire risk prediction pipeline:

1. Imputation
---------------
To run imputation import the imputation task::

    from thehonestgenepipeline.imputation import imputation
    # assuming that genotype.hdf5 is located in the ORIGINAL folder
    res = imputation.delay('genotype.hdf5')
    # wait until job is finished and retrieve some statistics about the imputation
    data = res.get()

2. Ancestry
----------------
After the genotype was imputed, ancestry analysis can be run by importing the ancestry task::

    from thehonestgenepipeline.ancestry import analysis
    # assuming that the imputed genotype.hdf5 is located in the IMPUTED folder
    res = analysis.delay('genotype.hdf5')
    # wait until job is finished and retrieve some statistics about the ancestry analysis
    data = res.get() 

3. Risk Prediction
------------------
As a final step after ancestry analysis, risk prediction can be run using the riskprediction task::

    TODO


Test
***********

The test suite can be run with::

      $ python setup.py test

Installation
***********

Of course, the recommended installation method is pip::

    $ pip install thehonestgene-pipeline

Thank You
***********

Thanks for checking this library out! We hope you find it useful.

Of course, there's always room for improvement. Feel free to `open an issue <https://github.com/TheHonestGene/thehonestgene-pipeline/issues>`_ so we can make it better.
