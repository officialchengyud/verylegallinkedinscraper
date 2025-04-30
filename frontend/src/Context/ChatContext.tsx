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
      sendChat(message.data, true);
      console.log("Received from server:", message.data);
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
