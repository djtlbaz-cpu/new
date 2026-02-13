
export const Button = ({ children, onClick, className = '', variant = 'default', disabled = false, ...props }) => {
  const baseStyles = 'px-4 py-2 rounded-md font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2'

  const variants = {
    default: 'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500',
    outline: 'border-2 border-gray-300 hover:bg-gray-100 text-gray-700 focus:ring-gray-500',
    ghost: 'hover:bg-gray-100 text-gray-700',
    destructive: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
  }

  const disabledStyles = disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variants[variant]} ${disabledStyles} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
