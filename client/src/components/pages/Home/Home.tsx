import { Button } from "@/components/ui/components/Button";
import Input from "@/components/ui/components/Input";
import { Copy } from "lucide-react";
import React, { useState } from "react";

const Pergunta = ({ children }: { children: string }) => {
  return (
    <div className="w-full flex justify-end">
      <p className="max-w-160 p-4 rounded-xl rounded-br-xs text-white bg-black">
        {children}
      </p>
    </div>
  );
};

const Resposta = ({ children }: { children: string }) => {
  return (
    <div className="w-full flex-col gap-2">
      <div className="flex flex-col gap-4">
        <p className="text-lg">{children}</p>
      </div>
      <div className="flex gap-2">
        <Button size="icon" className="size-8" variant="ghost">
          <Copy size={22} />
        </Button>
      </div>
    </div>
  );
};

const Home = () => {
  const [text, setText] = useState<boolean>(false);
  const [search, setSearch] = useState<string>("");


  const handleSubmit = (e:React.FormEvent) =>{
    e.preventDefault();

    if(!search.trim()) return;

    setText((prev)=> !prev);
  }

  return (
    <div className="w-full flex px-10 justify-center">
      <div className="w-full py-10 max-w-[1100px] flex flex-col justify-center items-center gap-6">
        {text ? (
          <div className="w-full flex-1 flex flex-col gap-8">
            <Pergunta>
              Identifique o touro que possui a maior média de lactação de suas
              filhas ao primeiro parto.
            </Pergunta>
            <Resposta>
              Lorem ipsum dolor sit amet consectetur, adipisicing elit.
              Voluptate nobis excepturi tempora. Esse nam quis molestiae illo
              vitae perspiciatis obcaecati aspernatur corrupti, doloremque atque
              laboriosam repudiandae quaerat aliquid consequatur commodi!
            </Resposta>
          </div>
        ) : (
          <header className="w-full">
            <p className="text-center text-5xl font-semibold">Chatbot bovino</p>
          </header>
        )}
        <form onSubmit={handleSubmit} className="w-full flex gap-4 items-center">
          <Input
            className="w-full rounded-full h-12 bg-white"
            placeholder="Qual sua pergunta?"
            value={search}
            onChange={(e)=>{
              const value = e.target.value;
              setSearch(value);
            }}
          />
          <Button type="submit">
            Enviar
          </Button>
        </form>
      </div>
    </div>
  );
};

export default Home;
