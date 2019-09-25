import argparse
def main():
    parser = argparse.ArgumentParser(description='Driver for ChaturCar')
    parser.add_argument('--hostname', default='0.0.0.0')
    parser.add_argument('--port', default=5000)
    parser.add_argument('--testing',default=True)
    parser.add_argument('--selfdrive',default=False)
    parser.add_argument('--collectdata',default=False)
    parser.add_argument('--record_time',default=10)
    parser.add_argument('--example', default='1')
    parser.add_argument('--framerate',default=30)
    args = parser.parse_args()

    print(args)

if __name__=="__main__":
        main()
