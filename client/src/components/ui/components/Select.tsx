
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { CircleQuestionMark } from "lucide-react";

export type Option = {
  key: string;
  value: string;
};



type SelectData = {
  options: Option[];
  selectedOption: string;
  setSelectedOption: (value: string) => void;
  placeholder: string;
  label: string;
  tip?: string;
  error?: string;
};

export const SelectData = ({
  options,
  selectedOption,
  setSelectedOption,
  placeholder,
  label,
  tip,
  error,
}: SelectData) => {
  return (
    <div className="w-full flex flex-col gap-1">
      {label && (
        <div className="flex w-full gap-2 items-center">
          <p className="text-sm font-medium">
            {label}
          </p>
          {tip && (
            <Tooltip>
              <TooltipTrigger asChild>
                <CircleQuestionMark size={15} />
              </TooltipTrigger>
              <TooltipContent align="center" className="max-w-48">
                <p>{tip}</p>
              </TooltipContent>
            </Tooltip>
          )}
        </div>
      )}
      <Select value={selectedOption} onValueChange={setSelectedOption}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            {options.map((item) => (
              <SelectItem key={item.key} value={item.key}>
                {item.value}
              </SelectItem>
            ))}
          </SelectGroup>
        </SelectContent>
      </Select>
      {error && <p className="text-red-500 font-normal text-sm">{error}</p>}
    </div>
  );
};
