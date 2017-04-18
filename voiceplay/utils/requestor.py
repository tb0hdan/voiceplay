#-*- coding: utf-8 -*-
""" HTTP Requestor module """

import json
import random
random.seed()

from voiceplay.logger import logger
from voiceplay.database import voiceplaydb
from .models import BaseCfgModel


class WSRequestor(BaseCfgModel):
    """
    Web service requestor.
    """
    headers = {'User-Agent': random.choice(['Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                                            'Mozilla/5.0 (MSIE 10.0; Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36 OPR/41.0.2353.69'])}

    def get_check_all(self):
        """
        Get results, use cache if needed.
        """
        result = voiceplaydb.get_cached_service(self.cache_file, expires=7)
        if result:
            logger.debug('Using %s cached version...', self.cache_file)  # pylint:disable=no-member
            result = json.loads(result)
        else:
            logger.debug('Fetching and storing fresh %s version...', self.cache_file)  # pylint:disable=no-member
            result = self.get_all()  # pylint:disable=no-member
            if result:
                voiceplaydb.set_cached_service(self.cache_file, json.dumps(result))
        return result
