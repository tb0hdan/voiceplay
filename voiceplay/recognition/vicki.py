class Vicki(object):
    '''
    Vicki main class
    '''

    def __init__(self):
        self.init_logger()
        self.rec = sr.Recognizer()
        self.tts = TextToSpeech()
        self.queue = Queue()
        self.shutdown = False
        self.logger.debug('Vicki init completed')
        self.player = VickiPlayer(tts=self.tts)

    def init_logger(self, name='Vicki'):
        '''
        Initialize logger
        '''
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler(sys.stderr)
        self.logger.addHandler(handler)

    def process_request(self, request):
        '''
        process request
        '''
        try:
            self.player.play_from_parser(request)
        except Exception as exc:
            self.logger.error(exc)
            self.tts.say_put('Vicki could not process your request')

    def wakeword_callback(self, message):
        print (message)
        self.wake_up = True

    def background_listener(self):
        msg = 'Vicki is listening'
        self.tts.say_put(msg)
        # TODO: Fix this using callback or something so that 
        # we do not record ourselves
        time.sleep(3)
        self.logger.warning(msg)
        self.wake_up = False
        while True:
            if self.shutdown:
                break

            if self.wake_up:
                self.logger.warning('Wake word!')
                self.tts.say_put('Yes')
                self.wake_up = False
            else:
                time.sleep(0.5)
                continue

            # command goes next
            with sr.Microphone() as source:
                audio = self.rec.listen(source)
            try:
                result = self.rec.recognize_google(audio)
            except sr.UnknownValueError:
                msg = 'Vicki could not understand audio'
                self.tts.say_put(msg)
                self.logger.warning(msg)
                result = None
            except sr.RequestError as e:
                msg = 'Recognition error'
                self.tts.say_put(msg)
                self.logger.warning('{0}; {1}'.format(msg, e))
                result = None
            if result:
                self.queue.put(result)

    def background_executor(self):
        while True:
            if self.shutdown:
                break
            if not self.queue.empty():
                message = self.queue.get()
                if message == 'shutdown':
                    self.shutdown = True
                    self.player.stop()
                else:
                    self.process_request(message)
            time.sleep(1)

    def background_speaker(self):
        self.tts.say_poll()

    def run_forever_new(self):
        '''
        Main loop
        '''
        listener = threading.Thread(name='BackgroundListener', target=self.background_listener)
        listener.setDaemon(True)

        player = threading.Thread(name='BackgroundPlayer', target=self.background_executor)
        player.setDaemon(True)

        speaker = threading.Thread(name='BackgroundSpeaker', target=self.background_speaker)
        speaker.setDaemon(True)

        listener.start()
        player.start()
        speaker.start()
        while True:
            if self.shutdown:
                break
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                self.shutdown = True  # for threads
                listener.join()
                player.join()
                speaker.join()
                break
