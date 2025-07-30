from cxglearner.utils.utils_config import DefaultConfigs
from cxglearner.config.config import Config
from cxglearner.utils.utils_log import init_logger
from cxglearner.parser.parser import UniParser


if __name__ == '__main__':
    config = Config(DefaultConfigs.eng)
    logger = init_logger(config)

    parser = UniParser(name_or_path="corpus/", config=config, logger=logger)

    raw_sentences = ['There are prepositive and postpositive attributes in terms of position.',
                     'what does it mean in terms of coffee in addition to cat?',
                     'waiting for next youtube video',
                     'what is your preference on this topic?',
                     'she should be more polite with the customers.']
    # raw_sentences.extend(['This functionality works by masking out threads that are not used. Therefore, the number of threads n must be less than or equal to NUMBA_NUM_THREADS, the total number of threads that are launched. See its documentation for more details.']*1000)
    res = parser.parse(raw_sentences)

    print(res[4])
