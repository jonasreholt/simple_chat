from socket import socket
import common.global_constants as GC

class Messenger:
    def __init__(self):
        self.messages = []

    def receive_msg(self, s: socket):
        """Waits for and retrieves message form s.

        Returns:
            str: decoded message retrieved. "" if no message or error
        """
        try:
            while (True):
                if len(self.messages) > 0 and GC.END_MARKER in self.messages[0]:
                    # messages already contains a whole element
                    break
                msg = s.recv(1024).decode("utf-8")
                if not msg: # End of file recieved
                    break
                self.messages.append(msg)
                if GC.END_MARKER in msg:
                    break
                elif len(self.messages) > 1:
                    last_pair = self.messages[-2] + self.messages[-1]
                    if GC.END_MARKER in last_pair:
                        break
            msg = "".join(self.messages)
            mark_idx = msg.find(GC.END_MARKER)
            self.messages = [msg[mark_idx + 1:]]
            return msg[:mark_idx]
        except Exception as e:
            print(">> could not recieve message: ", e)
            return ""

    def send_msg(self, s: socket, msg: str):
        """Sends msg as utf-8 encoded bytes to self.name_server.
        (If sendall() fails on the background of lost connection,
        it tries to reconect)

        Args:
            msg (str): msg to encode and send
        """
        try:
            s.sendall(bytes(msg + GC.END_MARKER, GC.ENCODING))
        except Exception as e:
            print(">> Could not send message: ", e)
