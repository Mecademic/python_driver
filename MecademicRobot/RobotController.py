import socket
import time

class RobotController:
    r"""Class for the Mecademic Robot allowing for communication and control of the 
    Mecademic Robot with all of its features available

    Attributes
    --------
        Address: str
            IP Address
        socket: socket
            socket connecting to physical Mecademic Robot
        EOB: int
            Setting for EOB reply
        EOM: int 
            Setting for EOM reply
        error: boolean
            Error Status of the Mecademic Robot
    """
    def __init__(self, address):
        r"""Constructor for an instance of the Class Mecademic Robot 

        Parameters
        --------
        address: str 
            The IP address associated to the Mecademic Robot
        """
        self.address = address
        self.socket = None
        self.EOB = 1
        self.EOM = 1
        self.error = False

    def isInError(self):
        r"""Status method that checks whether the Mecademic Robot is in error mode.

        Returns
        --------
        error: boolean 
            Returns the error flag
        """
        return self.error               #return the global variable error, which is updated by the other methods

    def ResetError(self):
        r"""Resets the error in the Mecademic Robot 

        Returns
        --------
        response : str
            response from the Robot
        """
        self.error = False
        cmd = "ResetError"
        response = self.exchangeMsg(cmd)
        reset_success = self._response_contains(response, ["The error was reset","There was no error to reset"])
        if reset_success:
            self.error = False
        else:
            self.error = True
        return response

    def Connect(self):
        r"""Connects Mecademic Robot object communication to the physical Mecademic Robot

        Returns
        --------
        status: boolean 
            Return whether the connection is established
        """
        try:
            self.socket = socket.socket()                   #Get a socket
            self.socket.settimeout(0.1)                     #set the timeout to 100ms
            try:
                self.socket.connect((self.address, 10000))  #connect to the robot's address
            except socket.timeout:                          #catch if the robot is not connected to in time
                raise TimeoutError                          
            # Receive confirmation of connection
            if self.socket is None:                         #check that socket is not connected to nothing
                raise RuntimeError
            self.socket.settimeout(10)                      #set timeout to 10 seconds
            try:    
                response = self.socket.recv(1024).decode("ascii")   #receive message from robot
            except socket.timeout:
                raise RuntimeError
            response_found = self._response_contains(response, ["[3000]"])  #search for key [3000] in the received packet
            if not response_found:
                raise RuntimeError
            else:
                return response_found                       #return if key was found in packet
        except TimeoutError:
            return False
        # OTHER USER !!!
        except RuntimeError:
            return False

    def Disconnect(self):
        r"""Disconnects Mecademic Robot object from physical Mecademic Robot
        """
        if(self.socket is not None):
            self.socket.close()
            self.socket = None

    @staticmethod
    def _response_contains(response, code_list):
        r"""Scans received response for code IDs

        Parameters
        --------
        response: str
            Message to scan for codes
        code_list: list of int 
            List of codes to look for in the response
        
        Returns
        --------
        response_found: boolean
            Returns whether the response contains a code ID of interest 
        """
        response_found = False
        for code in code_list:
            if response.find(code) != -1:
                response_found = True
                break
        return response_found
    
    def _send(self, cmd):
        r"""Sends a command to the physical Mecademic Robot

        Parameters
        --------
        cmd: str 
            Command to be sent

        Returns
        --------    
        status: boolean
            Returns whether the message is sent
        """
        if self.socket is None or self.error:               #check that the connection is established or the robot is in error
            return False                                    #if issues detected, no point in trying to send a cmd that won't reach the robot
        cmd = cmd + '\0'
        status = 0
        while status == 0:
            try:                                  #while the message hasn't been sent
                status = self.socket.send(cmd.encode("ascii"))  #send command in ascii encoding
            except:
                break
            if status != 0:
                return True                                 #return true when the message has been sent 
        #Message failed to be sent, return false
        return False        

    def _receive(self, answer_list, delay):
        r"""Receives message from the Mecademic Robot and 
        looks for expected answer in the reply

        Parameters
        --------
        answer_list: list of int
            codes to look for in the response
        delay: int
            time to set for timeout of the socket
        
        Returns
        --------
        response: str
            Response received from Mecademic Robot
        """
        if self.socket is None:                         #check that the connection is established
            return                                      #if no connection, nothing to receive
        response_list = []                              
        response_found = False
        for x in answer_list:                           #convert codes to search for in answer into comparable format
            response_list.append("["+str(x)+"]")
        error_found = False
        error_list = ["["+str(i)+"]" for i in range(1000, 1039)]+["["+str(i)+"]" for i in [3001,3003,3005,3009,3014,3026]]  #Make error codes in a comparable format
        self.socket.settimeout(delay)                   #set read timeout to desired delay
        while not response_found and not error_found:   #while no answers have been received, keep looking
            try:
                response = self.socket.recv(1024).decode("ascii")   #read message from robot
            except socket.timeout:
                return                                  #if timeout reached, either connection lost or nothing was sent from robot (damn disabled EOB and EOM)
            if(len(response_list)!=0):                  #if the message has a code to look for, find them
                response_found = self._response_contains(response, response_list)
            error_found = self._response_contains(response, error_list) #search message for errors
        if error_found:                                 #if errors have been found, flag the script
            self.error = True
        return response                                 #return the retrieved message

    def exchangeMsg(self, cmd, delay = 20, decode=True):
        r"""Sends and receives with the Mecademic Robot

        Parameters
        --------
        cmd: str
            Command to send to the Mecademic Robot
        delay: int
            timeout to set for the socket
        
        Returns
        --------
        response: str
            Response with desired code ID
        """
        response_list = self._getAnswerList(cmd)
        if(not self.error):                                 #if there is no error
            status = self._send(cmd)                        #send the command to the robot
            if status is True:                           #if the command was sent
                answer = self._receive(response_list, delay)#get response from robot
                if answer is not None:                      #if message was retrieved
                    for response in response_list:          #search for response codes
                        if self._response_contains(answer, [str(response)]): 
                            if(decode):
                                return self._decodeMsg(answer, response)   #decrypt response based on right response code
                            else:
                                return answer
                    error_list = [str(i) for i in range(1000, 1039)]+[str(i) for i in [3001,3003,3005,3009,3014,3026]]  #Make error codes in a comparable format
                    for response in error_list:
                        if self._response_contains(answer, [str(response)]): 
                            if(decode):
                                return self._decodeMsg(answer, response)   #decrypt response based on right response code
                            else:
                                return answer
                else:
                    if(len(response_list) == 0):            #if we aren't expecting anything, don't bother looking
                        return
                    else:
                        return

            #if message didn't send correctly, reboot communication
            self.Disconnect()
            time.sleep(1)
            self.Connect()
            return

    def _buildCommand(self, cmd, arg_list = []):
        r"""Builds the command string to send to the Mecademic Robot
        from the function name and arguments the command needs

        Parameters
        ---------
        cmd: str
            command name to send to the Mecademic Robot
        arg_list: list
            arguments the command requires to concatenate to the command
        
        Returns
        --------
        command: str 
            final command for the Mecademic Robot
        """
        command = cmd
        if(len(arg_list)!=0):
            command = command + '('
            for index in range(0, (len(arg_list)-1)):
                command = command+str(arg_list[index])+','
            command = command+str(arg_list[-1])+')'
        return command

    def _decodeMsg(self,response, response_key):
        r"""Decrypt information from the Mecademic Robot response to useful information
        that can be manipulated

        Parameters
        --------
        response: str 
            Response from the Mecademic Robot
        response_key: int 
            Code ID of response to decrypt
        
        Returns
        --------
        code: str, tuple of floats or tuple of ints
            Decrypted information in the format that best fits the raw message
        """
        code = response.replace("["+str(response_key)+"][", "").replace("]", "").replace("\x00", "")    #remove delimiters and \x00 bytes
        code_list = code.split(",")                         #split packets into their individual selves
        if(response_key == 2026 or response_key == 2027):   #if expected packet is from GetJoints (2026) or GetPose (2027), rest of packet is position data 
            code_list_float = tuple((float(x) for x in code_list))      #convert position data to floats
            return code_list_float
        elif(response_key == 2029 or response_key == 2007 or response_key == 2079): #if expected packet is from GetConf (2029), GetStatusRobot (2007) or GetStatusGripper (2079), rest of packet is data
            code_list_int = tuple((int(x) for x in code_list))          #convert status data into integers
            return code_list_int
        else:
            return code                                      #nothing to decrypt or decryption not specified

    def _getAnswerList(self, command):
        r"""Retrieve the expected answer codes that the Mecademic Robot should send as feedback after
        a command.

        Parameters
        --------
        command: str
            command that is to be sent to the Mecademic Robot

        Returns
        --------
        answer_list: list of ints
            list of answer codes to search for in response
        """
        if(command.find('ActivateRobot') != -1):
            return [2000,2001]
        elif(command.find('ActivateSim')!= -1):
            return [2045]
        elif(command.find('ClearMotion')!= -1):
            return [2044]
        elif(command.find("DeactivateRobot")!= -1):
            return [2004]
        elif(command.find("BrakesOn")!= -1):
            return [2010]
        elif(command.find("BrakesOff")!= -1):
            return [2008]
        elif(command.find("GetConf")!= -1):
            return [2029]
        elif(command.find('GetJoints')!= -1):
            return [2026]
        elif(command.find('GetStatusRobot')!= -1):
            return [2007]
        elif(command.find('GetStatusGripper')!= -1):
            return [2079]
        elif(command.find('GetPose')!= -1):
            return [2027]
        elif(command.find('Home')!= -1):
            return [2002,2003]
        elif(command.find('PauseMotion')!= -1):
            answer_list = [2042]
            if(self.EOM == 1): 
                answer_list.append(3004)
            return answer_list
        elif(command.find('ResetError')!= -1):
            return [2005,2006]
        elif(command.find('ResumeMotion')!= -1):
            return [2043]
        elif(command.find('SetEOB')!= -1):
            return [2054,2055]
        elif(command.find('SetEOM')!= -1):
            return [2052,2053]
        else:
            answer_list = []
            if(self.EOB==1):
                answer_list.append(3012)
            if(self.EOM==1):
                for name in ['MoveJoints','MoveLin','MoveLinRelTRF','MoveLinRelWRF','MovePose','SetCartAcc','SetJointAcc','SetTRF','SetWRF']:
                    if(command.find(name) != -1):
                        answer_list.append(3004)
                        break
            return answer_list

    def Activate(self):
        r"""Activates the Mecademic Robot 

        Returns
        --------
        response: str
            received decrypted response
        """
        cmd = "ActivateRobot"
        return self.exchangeMsg(cmd)

    def Deactivate(self):
        """Deactivates the Mecademic Robot 

        Returns
        --------
        response: str
            received decrypted response
        """
        cmd = "DeactivateRobot"
        return self.exchangeMsg(cmd)

    def ActivateSim(self):
        r"""Activates the Mecademic Robot simulation mode 

        Returns
        --------
        response: str
            received decrypted response
        """
        cmd = "ActivateSim"
        return self.exchangeMsg(cmd)

    def DeactivateSim(self):
        r"""Deactivate the Mecademic Robot simulation mode 

        Returns
        --------
        response: str
            received decrypted response
        """
        cmd = "DeactivateSim"
        return self.exchangeMsg(cmd)

    def SwitchToEtherCAT(self):
        r"""Places the Mecademic Robot in EtherCat mode

        Returns
        --------
        response: str
            received decrypted response
        """
        cmd = "SwitchToEtherCAT"
        return self.exchangeMsg(cmd)
    
    def SetEOB(self, e):
        r"""Sets End of Block answer active or inactive in the Mecademic Robot

        Parameters
        --------
        e: int
            Enables (1) EOB or Disables (0) EOB

        Returns
        --------
        response: str
            received decrypted response
        """
        if(e == 1):
            self.EOB = 1
        else:
            self.EOB = 0
        raw_cmd = "SetEOB"
        cmd = self._buildCommand(raw_cmd,[e])
        return self.exchangeMsg(cmd)
        
    def SetEOM(self, e):
        r"""Sets End of Movement answer active or inactive in the Mecademic Robot
        
        Parameters
        --------
        e: int 
            Enables (1) EOM or Disables (0) EOM
        
        Returns
        --------
        response: str
            received decrypted response
        """
        if(e == 1):
            self.EOM = 1
        else:
            self.EOM = 0
        raw_cmd = "SetEOM"
        cmd = self._buildCommand(raw_cmd,[e])
        return self.exchangeMsg(cmd)    

    def Home(self):
        r"""Homes the Mecademic Robot

        Returns
        --------
        response: str
            received decrypted response
        """
        cmd = "Home"
        return self.exchangeMsg(cmd)

    def Delay(self, t):
        r"""Gives the Mecademic Robot a wait time before performing another action

        Parameters
        --------
        t : float or int
            time to delay the Robot
        
        Returns
        --------
        response: str
            received decrypted response
        """
        if(not isinstance(t,float)):
            t = float(t)
        raw_cmd = "delay"
        cmd = self._buildCommand(raw_cmd,[t])
        return self.exchangeMsg(cmd, t*2)

    def GripperOpen(self):
        r"""Opens the gripper of the end-effector

        Returns
        --------
        response: str
            received decrypted response
        """
        cmd = 'GripperOpen'
        return self.exchangeMsg(cmd)

    def GripperClose(self):
        r"""Closes the gripper of the end-effector

        Returns
        --------
        response: str
            received decrypted response
        """
        cmd = 'GripperClose'
        return self.exchangeMsg(cmd)

    def MoveJoints(self, theta_1, theta_2, theta_3, theta_4, theta_5, theta_6):
        r"""Moves the joints of the Mecademic Robot to the desired angles
        
        Parameters
        --------
        theta_1: float or int
            Angle of joint 1
        theta_2: float or int
            Angle of joint 2
        theta_3: float or int
            Angle of joint 3
        theta_4: float or int
            Angle of joint 4
        theta_5: float or int
            Angle of joint 5
        theta_6: float or int
            Angle of joint 6

        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "MoveJoints"
        cmd = self._buildCommand(raw_cmd,[theta_1,theta_2,theta_3,theta_4,theta_5,theta_6])
        return self.exchangeMsg(cmd)

    def MoveLin(self, x, y, z, alpha, beta, gamma):
        r"""Moves the Mecademic Robot tool reference in a straight line to final
        point with specified direction

        Parameters
        --------
        x: float or int
            Final x coordinate
        y: float or int
            Final y coordinate
        z: float or int
            Final z coordinate
        alpha: float or int
            Final Alpha angle
        beta: float or int
            Final Beta angle
        gamma: float or int
            Final Gamma angle

        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "MoveLin"
        cmd = self._buildCommand(raw_cmd,[x,y,z,alpha,beta,gamma])
        return self.exchangeMsg(cmd)

    def MoveLinRelTRF(self, x, y, z, alpha, beta, gamma):
        r"""Moves the Mecademic Robot tool reference frame to specified coordinates and heading

        Parameters
        --------
        x: float or int
            New Reference x coordinate
        y: float or int
            New Reference y coordinate
        z: float or int
            New Reference z coordinate
        alpha: float or int
            New Reference Alpha angle
        beta: float or int
            New Reference Beta angle
        gamma: float or int
            New Reference Gamma angle

        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "MoveLinRelTRF"
        cmd = self._buildCommand(raw_cmd,[x,y,z,alpha,beta,gamma])
        return self.exchangeMsg(cmd)

    def MoveLinRelWRF(self, x, y, z, alpha, beta, gamma):
        r"""Moves the Mecademic Robot world reference frame to specified coordinates and heading

        Parameters
        --------
        x: float or int
            New Reference x coordinate
        y: float or int
            New Reference y coordinate
        z: float or int
            New Reference z coordinate
        alpha: float or int
            New Reference Alpha angle
        beta: float or int
            New Reference Beta angle
        gamma: float or int
            New Reference Gamma angle

        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "MoveLinRelWRF"
        cmd = self._buildCommand(raw_cmd,[x,y,z,alpha,beta,gamma])
        return self.exchangeMsg(cmd)

    def MovePose(self, x, y, z, alpha, beta, gamma):
        r"""Moves the Mecademic Robot joints to have the TRF at (x,y,z)
        with heading (alpha, beta, gamma)

        Parameters
        --------
        x: float or int
            Final x coordinate
        y: float or int
            Final y coordinate
        z: float or int
            Final z coordinate
        alpha: float or int
            Final Alpha angle
        beta: float or int
            Final Beta angle
        gamma: float or int
            Final Gamma angle

        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "MovePose"
        cmd = self._buildCommand(raw_cmd,[x,y,z,alpha,beta,gamma])
        return self.exchangeMsg(cmd)

    def SetBlending(self, p):
        r"""Sets the blending of the Mecademic Robot
        
        Parameters
        --------
        p: int
            Enable(1-100)/Disable(0) Mecademic Robot's blending
        
        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "SetBlending"
        cmd = self._buildCommand(raw_cmd,[p])
        return self.exchangeMsg(cmd)

    def SetAutoConf(self, e):
        r"""Enables or Disables the automatic robot configuration 
        selection and has effect only on the MovePose command
        
        Parameters
        --------
        e: int
            Enable(1)/Disable(0) Mecademic Robot's automatic configuration selection
        
        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "SetAutoConf"
        cmd = self._buildCommand(raw_cmd,[e])
        return self.exchangeMsg(cmd)

    def SetCartAcc(self, p):
        r"""Sets the cartesian accelerations of the linear and angular movements of the 
        Mecademic Robot end effector

        Parameters
        --------
        p: int
            value between 1 and 100
        
        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "SetCartAcc"
        cmd = self._buildCommand(raw_cmd,[p])
        return self.exchangeMsg(cmd)

    def SetCartAngVel(self, w):
        r"""Sets the cartesian angular velocity of the Mecademic Robot TRF with respect to its WRF

        Parameters
        --------
        w: float or int
            value between 0.001 and 180
        
        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "SetCartAngVel"
        cmd = self._buildCommand(raw_cmd,[w])
        return self.exchangeMsg(cmd)

    def SetCartLinVel(self, v):
        r"""Sets the cartesian linear velocity of the Mecademic Robot's TRF relative to its WRF

        Parameters
        --------
        v: float or int
            value between 0.001 and 500

        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "SetCartLinVel"
        cmd = self._buildCommand(raw_cmd,[v])
        return self.exchangeMsg(cmd)

    def SetConf(self, c1, c3, c5):
        r"""Sets the desired Mecademic Robot inverse kinematic configuration to be observed in the 
        MovePose command

        Parameters
        --------
        c1: int 
            -1 or 1
        c3: int 
            -1 or 1
        c5: int 
            -1 or 1
        
        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "SetConf"
        cmd = self._buildCommand(raw_cmd,[c1,c3,c5])
        return self.exchangeMsg(cmd)
    
    def SetGripperForce(self, p):
        r"""Sets the Gripper's grip force

        Parameters
        --------
        p: int
            value between 1 to 100
        
        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "SetGripperForce"
        cmd = self._buildCommand(raw_cmd,[p])
        return self.exchangeMsg(cmd)

    def SetGripperVel(self, p):
        r"""Sets the Gripper fingers' velocity with respect to the gripper

        Parameters
        --------
        p: int
            value between 1 to 100
        
        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "SetGripperVel"
        cmd = self._buildCommand(raw_cmd,[p])
        return self.exchangeMsg(cmd)
    
    def SetJointAcc(self, p):
        r"""Sets the acceleration of the joints

        Parameters
        --------
        p: int
            value between 1 to 100
        
        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "SetJointAcc"
        cmd = self._buildCommand(raw_cmd,[p])
        return self.exchangeMsg(cmd)
    
    def SetJointVel(self, velocity):
        r"""Sets the angular velocities of the Mecademic Robot's joints

        Parameters
        --------
        velocity: int
            value between 1 to 100
        
        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "SetJointVel"
        cmd = self._buildCommand(raw_cmd,[velocity])
        return self.exchangeMsg(cmd)

    def SetTRF(self, x, y, z, alpha, beta, gamma):
        r"""Sets the Mecademic Robot TRF at (x,y,z) and heading (alpha, beta, gamma)
        with respect to the FRF

        Parameters
        --------
        x: float or int
            Final x coordinate
        y: float or int
            Final y coordinate
        z: float or int
            Final z coordinate
        alpha: float or int
            Final Alpha angle
        beta: float or int
            Final Beta angle
        gamma: float or int
            Final Gamma angle
        
        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "SetTRF"
        cmd = self._buildCommand(raw_cmd,[x,y,z,alpha,beta,gamma])
        return self.exchangeMsg(cmd)
    
    def SetWRF(self, x, y, z, alpha, beta, gamma):
        r"""Sets the Mecademic Robot WRF at (x,y,z) and heading (alpha, beta, gamma)
        with respect to the BRF

        Parameters
        --------
        x: float or int
            Final x coordinate
        y: float or int
            Final y coordinate
        z: float or int 
            Final z coordinate
        alpha: float or int 
            Final Alpha angle
        beta: float or int
            Final Beta angle
        gamma: float or int
            Final Gamma angle
        
        Returns
        --------
        response: str
            received decrypted response
        """
        raw_cmd = "SetWRF"
        cmd = self._buildCommand(raw_cmd,[x,y,z,alpha,beta,gamma])
        return self.exchangeMsg(cmd)

    def GetStatusRobot(self):
        r"""Retrieves the robot status of the Mecademic Robot 

        Returns
        --------
        status: tuple of int
            status of Activation, Homing, Simulation, Error, Paused, EOB and EOM
        """
        received = None
        while received is None:
            cmd = "GetStatusRobot"
            received = self.exchangeMsg(cmd)
        code_list_int = received
        return {"Activated": code_list_int[0],
                "Homing": code_list_int[1],
                "Simulation": code_list_int[2],
                "Error": code_list_int[3],
                "Paused": code_list_int[4],
                "EOB": code_list_int[5],
                "EOM": code_list_int[6]}
    
    def GetStatusGripper(self):
        r"""Retrieves the gripper status of the Mecademic Robot 

        Returns
        --------
        status: tuple of int
            status of Gripper enabled, Homing state, Holding part, 
            Limit reached, Error state and force overload
        """
        received = None
        while received is None:
            cmd = "GetStatusGripper"
            received = self.exchangeMsg(cmd)
        code_list_int = received
        return {"Gripper enabled": code_list_int[0],
                "Homing state": code_list_int[1],
                "Holding part": code_list_int[2],
                "Limit reached": code_list_int[3],
                "Error state": code_list_int[4],
                "force overload": code_list_int[5]}

    def GetConf(self):
        r"""Retrieves the current inverse kinematic configuration

        Returns
        --------
        response: str
            received decrypted response
        """
        cmd = "GetConf"
        return self.exchangeMsg(cmd)

    def GetJoints(self):
        r"""Retrieves the Mecademic Robot joint angles in degrees

        Returns
        --------
        response: str
            received decrypted response
        """
        cmd = "GetJoints"
        return self.exchangeMsg(cmd)

    def GetPose(self):
        r"""Retrieves the current pose of the Mecademic Robot TRF with
        respect to the WRF

        Returns
        --------
        response: str
            received decrypted response
        """
        cmd = "GetPose"
        return self.exchangeMsg(cmd)

    def PauseMotion(self):
        r"""Stops the robot movement and holds until ResumeMotion

        Returns
        --------
        response: str
            received decrypted response
        """
        cmd = "PauseMotion"
        return self.exchangeMsg(cmd)

    def ResumeMotion(self):
        r"""Resumes the robot movement after being Paused from PauseMotion
        or ClearMotion

        Returns
        --------
        response: str
            received decrypted response
        """
        cmd = "ResumeMotion"
        return self.exchangeMsg(cmd)

    def ClearMotion(self):
        r"""Stops the robot movement and deletes the rest of the robot's
        trajectory. Holds until a ResumeMotion

        Returns
        --------
        response: str
            received decrypted response
        """
        cmd = "ClearMotion"
        return self.exchangeMsg(cmd)

    def BrakesOn(self):
        r"""These commands enables the brakes of joints 1, 2 and 3,
        if and only if the robot is powered but deactivated.
        
        Returns
        --------
        response: str
            received decrypted response
        """
        cmd = "BrakesOn"
        return self.exchangeMsg(cmd)
    
    def BrakesOff(self):
        r"""These commands disables the brakes of joints 1, 2 and 3,
        if and only if the robot is powered but deactivated.
        
        Returns
        --------
        response: str
            received decrypted response
        """
        cmd = "BrakesOff"
        return self.exchangeMsg(cmd)
