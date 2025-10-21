import { Textarea } from "../textarea";

type textar = {
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
  label?: string;
  error?: string;
};

export const TextArea = ({
  placeholder,
  value,
  onChange,
  label,
  error,
}: textar) => {
  return (
    <div className="w-full flex flex-col gap-1">
      {label && <p className="text-sm font-medium">{label}</p>}
      <Textarea
        placeholder={placeholder}
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
        }}
        className="min-h-40"
      />
      {error && <p className="text-red-500 font-normal text-sm">{error}</p>}
    </div>
  );
};
