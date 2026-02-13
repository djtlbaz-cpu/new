
export const Slider = ({ value = [50], onValueChange, min = 0, max = 100, step = 1, className = '', ...props }) => {
  const handleChange = (e) => {
    if (onValueChange) {
      onValueChange([parseInt(e.target.value)])
    }
  }

  const percentage = ((Array.isArray(value) ? value[0] : value) - min) / (max - min) * 100

  return (
    <div className="relative w-full">
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={Array.isArray(value) ? value[0] : value}
        onChange={handleChange}
        className={`w-full h-3 bg-slate-700 rounded-full appearance-none cursor-pointer slider-modern ${className}`}
        style={{
          background: `linear-gradient(to right, rgb(59, 130, 246) 0%, rgb(147, 51, 234) ${percentage}%, rgb(51, 65, 85) ${percentage}%, rgb(51, 65, 85) 100%)`
        }}
        {...props}
      />
    </div>
  )
}
