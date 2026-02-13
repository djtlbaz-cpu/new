
export const Progress = ({ value = 0, max = 100, className = '', ...props }) => {
  const percentage = (value / max) * 100

  return (
    <div className={`w-full bg-gray-200 rounded-full h-2 overflow-hidden ${className}`} {...props}>
      <div
        className="bg-blue-600 h-full transition-all duration-300 ease-in-out"
        style={{ width: `${percentage}%` }}
      />
    </div>
  )
}
