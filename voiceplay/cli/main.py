from .argparser.argparser import MyArgumentParser

def main():
    parser = MyArgumentParser()
    parser.configure()
    parser.parse()

if __name__ == '__main__':
    main()