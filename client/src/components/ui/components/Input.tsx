import * as React from "react";
import { Input as InputBase } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button, buttonVariants } from "@/components/ui/components/Button";
import { type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { CircleQuestionMark, X } from "lucide-react";

import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

type ClearTextProps =
  | { clearText?: false; onClearText?: never } // Se clearText for false ou não existir, onClearText é proibido
  | { clearText: true; onClearText: () => void }; // Se clearText for true, onClearText é obrigatório

type InputBaseProps = React.InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
  classNameContainer?: string;
  tip?: string;
};

type DefaultInputProps = {
  variant?: "default";
  onSearchClick?: never; // Garante que onSearchClick não pode ser passado para a variante default
  variantButton?: never;
};

type SearchInputProps = {
  variant: "search";
  onSearchClick: (e: React.MouseEvent<HTMLButtonElement>) => void; // onSearchClick é OBRIGATÓRIO para a variante search
  variantButton?: VariantProps<typeof buttonVariants>["variant"]; // OBRIGATÓRIO também, mas pra ficar bonitinho e convencional
};

type InputProps = InputBaseProps &
  (DefaultInputProps | SearchInputProps) &
  ClearTextProps;

const Input = React.forwardRef<HTMLInputElement, InputProps>((props, ref) => {
  const { id, label, error, icon, className, classNameContainer, tip } = props; // Importante

  const [clearTextHab, setClearTextHab] = React.useState(false);

  const {
    variant = "default",
    onSearchClick,
    variantButton = "default",
    clearText = false,
    onClearText,
    ...rest
  } = props; // Estilização

  return (
    <div
      className={cn(
        "w-full transition-[width] relative flex gap-1 flex-col",
        classNameContainer
      )}
    >
      {label && (
        <div className="flex w-full gap-2 items-center">
          <Label htmlFor={id} className="text-sm">
            {label}
          </Label>
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
      <div className="flex flex-1 gap-2 items-center">
        <div className={cn("flex flex-1 relative items-center justify-center")}>
          <InputBase
            ref={ref}
            id={id}
            {...rest}
            className={cn(icon && "pr-15", className)}
            onFocus={() => setClearTextHab(true)}
            onBlur={() => setClearTextHab(false)}
          />
          {clearText && clearTextHab && (
            <p
              className={cn(
                "absolute right-4 cursor-pointer",
                icon && "right-10"
              )}
              onClick={onClearText}
            >
              <X size={14} className="text-red-700" />
            </p>
          )}
          {icon && (
            <p className="absolute right-2 pointer-events-none">{icon}</p>
          )}
        </div>
        {variant === "search" && (
          <Button variant={variantButton} onClick={onSearchClick}>
            Buscar
          </Button>
        )}
      </div>
      {error && <p className="text-red-500 font-normal text-sm">{error}</p>}
    </div>
  );
});

Input.displayName = "Input";

export default Input;
