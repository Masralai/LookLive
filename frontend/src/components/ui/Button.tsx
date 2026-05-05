interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "ghost" | "primary";
  children: React.ReactNode;
}

export function Button({ variant = "ghost", className = "", children, ...props }: ButtonProps) {
  const baseStyles = "inline-flex items-center justify-center font-medium transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-lime-spritz focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
  
  const variants = {
    ghost: "bg-transparent border border-ash-border rounded-[999px] px-4 py-2 text-ink-black hover:bg-e6e6e6",
    primary: "bg-light-lime border border-lime-spritz rounded-[999px] px-4 py-2 text-ink-black hover:opacity-90",
  };

  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}