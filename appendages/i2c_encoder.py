class I2CEncoder:
    def interact(self, parseResults):
        def help(name):
            self.__dict__["help_" + name]()

        name = parseResults.parsed[0]
        args = parseResults.parsed[1].split()

        if len(args) == 0:
            help(name)

        elif args[0] == "set_pid_source":
            pid_source = args[1]

            if pid_source not in ["position", "velocity"]:
                help(name)
                return

            self.s.get_appendage(name).set_pid_source(pid_source)

        elif args[0] == "get_position":
            val = self.s.get_appendage(name).get_position()
            print("{}: {}".format(name, val))

        elif args[0] == "set_position":
            try:
                pos = float(args[1])
            except ValueError:
                help(name)
                return

            self.s.get_appendage(name).set_position(Angle(pos, Angle.rev))

        elif args[0] == "raw_position":
            val = self.s.get_appendage(name).raw_position()
            print("{}: {}".format(name, val))

        elif args[0] == "get_speed":
            val = self.s.get_appendage(name).get_speed()
            print("{}: {}".format(name, val))

        elif args[0] == "set_velocity":
            try:
                vel = float(args[1])
            except ValueError:
                help(name)
                return

            self.s.get_appendage(name).set_velocity(AngularVelocity(vel, AngularVelocity.rpm))

        elif args[0] == "get_velocity":
            val = self.s.get_appendage(name).get_velocity()
            print("{}: {}".format(name, val))

        elif args[0] == "zero":
            self.s.get_appendage(name).zero()

        elif args[0] == "pid_get":
            val = self.s.get_appendage(name).pid_get()
            print("{}: {}".format(name, val))

        else:
            help(name)

    def help(self):
        print("usage: <fwd:str> set_pid_source <source:str>")
        print("       <fwd:str> get_position")
        print("       <fwd:str> set_position <position:float>")
        print("       <fwd:str> raw_position")
        print("       <fwd:str> get_speed")
        print("       <fwd:str> set_velocity <velocity:float>")
        print("       <fwd:str> get_velocity")
        print("       <fwd:str> zero")
        print("       <fwd:str> pid_get")
        print("")
        print("pid_source: [\"position\", \"velocity\"]")
        print("position: rev")
        print("velocity: rpm")

    def complete(self, text, line, begidx, endidx):
        return [i for i in ["set_pid_source", "get_position", "set_position",
                            "raw_position", "get_speed", "set_velocity",
                            "get_velocity", "zero", "pid_get"] if i.startswith(text)]

