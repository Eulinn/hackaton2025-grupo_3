import { Button } from "@/components/ui/components/Button";
import Input from "@/components/ui/components/Input";
import { showErrorToast } from "@/lib/toastify";
import { Copy } from "lucide-react";
import React, { useState, type ReactNode } from "react";
import axios from "axios";

type PerguntaMsg = {
  tipo: "pergunta";
  texto: string;
};

type RespostaMsg = {
  tipo: "resposta";
  // Usamos 'any' para flexibilidade total no Hackathon
  // (significa "qualquer coisa": string, dict, list, etc.)
  dados: any;
};

type MensagemChat = PerguntaMsg | RespostaMsg;

const Pergunta = ({ children }: { children: ReactNode }) => {
  return (
    <div className="w-full flex justify-end">
      <p className="max-w-160 p-4 rounded-xl rounded-br-xs text-white bg-black">
        {children}
      </p>
    </div>
  );
};

const Resposta = ({ children }: { children: ReactNode }) => {
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
  const [search, setSearch] = useState<string>("");
  const [historico, setHistorico] = useState<MensagemChat[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!search.trim()) return;

    const perguntaAtual = search;
    // 1. Cria o objeto da PERGUNTA
    const novaPergunta: PerguntaMsg = {
      tipo: "pergunta",
      texto: perguntaAtual,
    };
    setHistorico((historicoAnterior) => [...historicoAnterior, novaPergunta]);
    setSearch("");
    setIsLoading(true);

    try {
      const payload = {
        query: search,
      };

      const response = await axios.post(
        "http://localhost:5000/api/nl-to-sql",
        payload
      );
      const novaResposta: RespostaMsg = {
        tipo: "resposta",
        dados: response.data,
      };

      setHistorico((historicoAnterior) => [...historicoAnterior, novaResposta]);
    } catch (error) {
      showErrorToast("Erro ao fazer consulta.");
      console.log(error);

      const erroResposta: RespostaMsg = {
        tipo: "resposta",
        dados: {
          error: true,
          message: "Desculpe, não consegui processar sua pergunta.",
        },
      };
      setHistorico((historicoAnterior) => [...historicoAnterior, erroResposta]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full flex px-10 justify-center">
      <div className="w-full py-10 max-w-[1100px] flex flex-col justify-center items-center gap-6">
        {historico.length > 0 ? (
          <div className="w-full flex-1 flex flex-col gap-8">
            {/* <Pergunta>
              Identifique o touro que possui a maior média de lactação de suas
              filhas ao primeiro parto.
            </Pergunta>
            <Resposta>
              Lorem ipsum dolor sit amet consectetur, adipisicing elit.
              Voluptate nobis excepturi tempora. Esse nam quis molestiae illo
              vitae perspiciatis obcaecati aspernatur corrupti, doloremque atque
              laboriosam repudiandae quaerat aliquid consequatur commodi!
            </Resposta> */}
            {historico.map((mensagem, index) => {
              if (mensagem.tipo === "pergunta") {
                return <Pergunta key={index}>{mensagem.texto}</Pergunta>;
              }

              if (mensagem.tipo === "resposta") {
                if (mensagem.dados?.success === false) {
                  // Tenta encontrar a melhor mensagem de erro
                  const errorMessage =
                    mensagem.dados.sql || // "Timeout: Ollama não respondeu a tempo"
                    mensagem.dados.error || // Se o backend enviar algo em 'error'
                    mensagem.dados.message || // Se o backend enviar algo em 'message'
                    "Ocorreu um erro desconhecido."; // Mensagem padrão

                  return (
                    <Resposta key={index}>
                      {/* Renderização "bonitinha" para o erro.
                  (Estou assumindo que você tem Tailwind; text-red-500 deixa vermelho)
                */}
                      <div className="text-red-500 p-2 rounded">
                        <p className="font-bold">Erro ao processar:</p>
                        <p>{errorMessage}</p>
                      </div>
                    </Resposta>
                  );
                }
                const dataArray = mensagem.dados?.results?.data;

                if (
                  mensagem.dados?.success === true &&
                  Array.isArray(dataArray) &&
                  dataArray.length > 0
                ) {
                  // 3. Se for um array de dados, renderiza de forma bonita
                  return (
                    <Resposta key={index}>
                      {/* Loop 1: Mapeia cada item no array 'data' (no seu ex, só tem 1) */}
                      {dataArray.map((registro, idx) => (
                        // 'registro' é o objeto: { codigo_touro: "...", nome_touro: "..." }
                        // Cria um container para cada registro (se houver múltiplos)
                        <div key={idx} className="mb-4 last:mb-0">
                          {/* Define um título se houver mais de um registro */}
                          {dataArray.length > 1 && (
                            <h4 className="font-bold mb-1">
                              Registro {idx + 1}
                            </h4>
                          )}

                          {/* Loop 2: Mapeia as chaves/valores do objeto (os "tópicos") */}
                          <ul className="list-disc list-inside space-y-1">
                            {Object.entries(registro).map(([key, value]) => (
                              <li key={key}>
                                {/* Formata a chave para ser mais legível (opcional) */}
                                <span className="capitalize font-semibold">
                                  {key.replace(/_/g, " ")}:
                                </span>
                                {/* Mostra o valor */}
                                <span className="ml-2">
                                  {value == null ? "Vazio" : String(value)}
                                </span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </Resposta>
                  );
                } else {
                  // 4. FALLBACK: Se 'data' estiver vazio, ou a resposta for um erro,
                  //    ou o formato for inesperado, mostra o JSON cru como antes.

                  const conteudoFormatado = JSON.stringify(
                    mensagem.dados,
                    null,
                    2
                  );

                  return (
                    <Resposta key={index}>
                      <pre className="text-sm whitespace-pre-wrap">
                        {conteudoFormatado}
                      </pre>
                    </Resposta>
                  );
                }
              }

              return null;
            })}
          </div>
        ) : (
          <header className="w-full">
            <p className="text-center text-5xl font-semibold">Chatbot bovino</p>
          </header>
        )}
        <form
          onSubmit={handleSubmit}
          className="w-full flex gap-4 items-center"
        >
          <Input
            className="w-full rounded-full h-12 bg-white"
            placeholder="Qual sua pergunta?"
            value={search}
            onChange={(e) => {
              const value = e.target.value;
              setSearch(value);
            }}
          />
          <Button loading={isLoading} type="submit">
            Enviar
          </Button>
        </form>
      </div>
    </div>
  );
};

export default Home;
