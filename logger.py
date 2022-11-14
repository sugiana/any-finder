from configparser import RawConfigParser
import logging
import logging.config


def setup_logging(conf_file):
    conf = RawConfigParser()
    conf.read(conf_file)
    d = {
        'version': 1,
        'formatters': {},
        'handlers': {},
        'loggers': {},
        }
    for section in conf.sections():
        if section.find('formatter_') == 0:
            name = section.split('formatter_')[1]
            data = {'format': conf.get(section, 'format')}
            d['formatters'][name] = data
        elif section.find('handler_') == 0:
            name = section.split('handler_')[1]
            data = {'formatter': conf.get(section, 'formatter')}
            data['class'] = 'logging.' + conf.get(section, 'class')
            if conf.has_option(section, 'stream'):
                data['stream'] = 'ext://' + conf.get(section, 'stream')
            else:
                data['filename'] = conf.get(section, 'filename')
            d['handlers'][name] = data
        elif section.find('logger_') == 0:
            name = section.split('logger_')[1]
            if name == 'root':
                name = ''
            data = {'level': conf.get(section, 'level')}
            value = conf.get(section, 'handlers')
            data['handlers'] = [x.strip() for x in value.split(',')]
            d['loggers'][name] = data
    logging.config.dictConfig(d)
