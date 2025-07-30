import sys

def __main():
    print('This is WIP...')

def main():
    try:
        __main()
    except Exception:
        import traceback
        print(traceback.format_exc, file=sys.stderr, end='')
        sts.exit(1)
    except KeyboardInterrupt:
        print('Interrupted by user', file=sys.stderr, end='')
        sts.exit(1)

if __name__ == '__main__':
    main()
