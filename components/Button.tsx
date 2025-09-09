
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
}

const Button: React.FC<ButtonProps> = ({ children, variant = 'primary', className, ...props }) => {
  const baseClasses = 'px-6 py-2.5 font-semibold rounded-md transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 flex items-center justify-center gap-2';

  const variantClasses = {
    primary: 'bg-cyan-500 text-white hover:bg-cyan-600 focus:ring-cyan-500 disabled:bg-gray-600 disabled:cursor-not-allowed',
    secondary: 'bg-gray-700 text-gray-200 hover:bg-gray-600 focus:ring-gray-500 disabled:bg-gray-800 disabled:text-gray-500 disabled:cursor-not-allowed',
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;
