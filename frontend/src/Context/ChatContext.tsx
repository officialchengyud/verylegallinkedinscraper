import React, {
  createContext,
  useContext,
  useState,
  ReactNode,
  useEffect,
  useRef,
} from "react";
import {
  Timestamp,
  doc,
  updateDoc,
  arrayUnion,
  getDoc,
} from "firebase/firestore";
import { db } from "../main";
import { useAuth } from "./AuthContext";
import { io, Socket } from "socket.io-client";
import { gapi } from "gapi-script";

const CLIENT_ID =
  "901374233553-08gidgm1omcqqrror03087d3qkpogjek.apps.googleusercontent.com";
const SCOPES = "https://www.googleapis.com/auth/gmail.send";

interface ChatMessage {
  role: string;
  message: string;
  timestamp: Timestamp;
}

interface ChatContextType {
  chatLog: ChatMessage[];
  getChat: () => void;
  sendChat: (message: string, agent?: boolean) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const { user, userInfo } = useAuth();
  const [chatLog, setChatLog] = useState<ChatMessage[]>([]);
  const [socket, setSocket] = useState<Socket | null>(null);
  const userRef = useRef(user);

  useEffect(() => {
    userRef.current = user;
  }, [user]);

  useEffect(() => {
    const initClient = () => {
      gapi.client
        .init({
          clientId: CLIENT_ID,
          discoveryDocs: [
            "https://www.googleapis.com/discovery/v1/apis/gmail/v1/rest",
          ],
          scope: SCOPES,
        })
        .then(() => {
          console.log("GAPI client initialized");
        })
        .catch((error: any) =>
          console.error("Error initializing GAPI client", error)
        );
    };

    gapi.load("client:auth2", initClient);
  }, []);

  const sendEmail = async (email: string, subject: string, message: string) => {
    try {
      const authInstance = gapi.auth2.getAuthInstance();
      const isSignedIn = authInstance.isSignedIn.get();

      if (!isSignedIn) {
        await authInstance.signIn();
      }

      const rawEmail = createEmail({
        to: email,
        from: "me",
        subject: subject,
        message,
      });

      await gapi.client.gmail.users.messages.send({
        userId: "me",
        resource: {
          raw: rawEmail,
        },
      });
    } catch (error) {
      console.error("Failed to send email:", error);
    }
  };

  const createEmail = ({
    to,
    from,
    subject,
    message,
  }: {
    to: string;
    from: string;
    subject: string;
    message: string;
  }): string => {
    const email = [
      `To: ${to}`,
      `From: ${from}`,
      `Subject: ${subject}`,
      "Content-Type: text/plain; charset=utf-8",
      "",
      message,
    ].join("\n");

    return btoa(unescape(encodeURIComponent(email)))
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");
  };

  const getChat = async () => {
    if (user) {
      const docRef = doc(db, "chats", user.uid);
      const docSnap = await getDoc(docRef);
      const messages = docSnap.exists() ? docSnap.data().messages : [];
      setChatLog(messages ?? []);
    }
  };

  const sendChat = (message: string, agent?: boolean) => {
    if (userRef.current?.uid) {
      console.log(message);
      const newMessage = {
        role: agent ? "agent" : "user",
        message: agent ? JSON.stringify(message) : message,
        timestamp: Timestamp.now(),
      };
      const docRef = doc(db, "chats", userRef.current?.uid);
      updateDoc(docRef, {
        messages: arrayUnion(newMessage),
      });
      setChatLog((chats) => [...chats, newMessage]);

      if (message === "start") {
        socket?.emit("initialize_agent", userInfo);
      } else {
        socket?.emit("user_input", { text: message, approved: false });
      }
    }
  };

  useEffect(() => {
    const newSocket = io("http://localhost:5000");
    setSocket(newSocket);

    newSocket.on("connect", () => {
      console.log("Connected to server");
    });

    newSocket.on("agent_initialized", () => {
      sendChat("We have recieved your information. You may continue.", true);
      console.log("Agent initialized");
    });

    newSocket.on("agent_output", (message) => {
      sendChat(message, true);
      console.log("Received from server:", JSON.stringify(message.data));
    });

    newSocket.on("send_email", (message) => {
      console.log("Send email:", message);
      sendEmail(message.email, message.subject, message.content);
    });

    newSocket.on("error", (message) => {
      console.log("error:", message.data);
    });

    newSocket.on("disconnect", () => {
      console.log("Disconnected from server");
    });

    // Clean up the socket connection when the component unmounts
    return () => {
      newSocket.disconnect();
    };
  }, []);

  useEffect(() => {
    if (user) {
      getChat();
    }
  }, [user]);

  return (
    <ChatContext.Provider value={{ chatLog, getChat, sendChat }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
};
