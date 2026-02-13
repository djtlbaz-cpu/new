
export const Card = ({ children, className = '', ...props }) => {
  return (
    <div className={`bg-gradient-to-br from-slate-700/95 to-slate-800/95 backdrop-blur-xl rounded-xl shadow-2xl border-2 border-slate-500/70 ${className}`} {...props}>
      {children}
    </div>
  )
}

export const CardHeader = ({ children, className = '', ...props }) => {
  return (
    <div className={`p-5 border-b-2 border-slate-500/60 bg-slate-700/70 ${className}`} {...props}>
      {children}
    </div>
  )
}

export const CardTitle = ({ children, className = '', ...props }) => {
  return (
    <h3 className={`text-xl font-bold text-white ${className}`} {...props}>
      {children}
    </h3>
  )
}

export const CardContent = ({ children, className = '', ...props }) => {
  return (
    <div className={`p-6 text-slate-100 ${className}`} {...props}>
      {children}
    </div>
  )
}
