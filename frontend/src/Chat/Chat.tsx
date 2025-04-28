import { Box, Button, Flex, TextArea, Text } from "@radix-ui/themes";
import { useEffect, useRef, useState } from "react";

const Chat = () => {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi there! How can I help you today?" },
  ]);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages([...messages, { role: "user", content: input }]);
    setInput("");
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "I'm working on it!" },
      ]);
    }, 1000);
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <Flex
      direction="column"
      style={{
        width: "100%",
        marginLeft: 250,
        maxHeight: "calc(100vh - 60px)",
      }}
    >
      <Flex
        direction="column"
        style={{
          flexGrow: 1,
          overflowY: "auto",
          padding: "20px",
          background: "#f9fafb",
        }}
      >
        {messages.map((msg, index) => (
          <Box
            key={index}
            style={{
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              background: msg.role === "user" ? "#4f46e5" : "#e5e7eb",
              color: msg.role === "user" ? "white" : "black",
              padding: "10px 15px",
              borderRadius: "20px",
              marginBottom: "10px",
              maxWidth: "70%",
              wordBreak: "break-word",
            }}
          >
            <Text>{msg.content}</Text>
          </Box>
        ))}
        <div ref={bottomRef} />
      </Flex>
      <Flex
        gap="2"
        align="center"
        style={{
          padding: "10px",
          borderTop: "1px solid #e5e7eb",
          background: "white",
        }}
      >
        <TextArea
          placeholder="Type your message..."
          style={{ width: "100%" }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        <Button onClick={handleSend}>Send</Button>
      </Flex>
    </Flex>
  );
};

export default Chat;
