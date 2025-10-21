import Input from "@/components/ui/components/Input";
import { useState } from "react";

const Home = () => {
  const [text, setText] = useState<string>("");

  return (
    <div className="w-full flex justify-center">
        <div className="w-full h-full py-15 max-w-[1100px] flex flex-col justify-center items-center gap-6">
          {text ? (
            <div className="w-full flex flex-col gap-2">
              <p className="w-full">
                Lorem ipsum dolor sit amet consectetur adipisicing elit.
                Perferendis voluptatibus iure, numquam, inventore expedita rem
                sunt debitis, aperiam molestiae placeat adipisci excepturi.
                Totam blanditiis reprehenderit eos vero provident, voluptatibus
                accusantium.
              </p>
            </div>
          ) : (
            <header className="w-full">
              <p className="text-center text-5xl font-semibold">
                Chatbot bovino
              </p>
            </header>
          )}
          <div className="w-full items-center">
            <Input
              className="w-full rounded-full h-12 bg-gray-100"
              placeholder="Qual sua pergunta?"
              variant="search"
              onSearchClick={() => {}}
            />
          </div>
        </div>
      </div>
  );
};

export default Home;
