import json
import os
import random
random.seed()
import time

from voiceplay.logger import logger
from voiceplay.config import Config
from .models import BaseCfgModel


class WSRequestor(BaseCfgModel):
    """
    Web service requestor.
    """
    headers = {'User-Agent': random.choice(['Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                                            'Mozilla/5.0 (MSIE 10.0; Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36 OPR/41.0.2353.69'
                                            ])}

    def get_check_all(self):
        """
        Get results, use cache if needed.
        """
        try:
            os.makedirs(os.path.expanduser(Config.persistent_dir))
        except Exception as exc:
            logger.debug('Persistent directory exists, good...')
        cache_file = os.path.expanduser(os.path.join(Config.persistent_dir, self.cache_file))  # pylint:disable=no-member
        # 1w cache
        if os.path.exists(cache_file) and time.time() - os.path.getmtime(cache_file) <= 3600 * 24 * 7:
            logger.debug('Using %s cached version...', self.cache_file)  # pylint:disable=no-member
            result = json.loads(open(cache_file, 'r').read())
        else:
            logger.debug('Fetching and storing fresh %s version...', self.cache_file)  # pylint:disable=no-member
            result = self.get_all()  # pylint:disable=no-member
            if result:
                with open(cache_file, 'w') as file_handle:
                    file_handle.write(json.dumps(result))
        return result
