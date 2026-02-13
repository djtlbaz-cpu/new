import { createContext, useContext, useState } from 'react'

const TabsContext = createContext()

export const Tabs = ({ children, defaultValue, value, onValueChange, className = '', ...props }) => {
  const [activeTab, setActiveTab] = useState(defaultValue || value || 'timeline')

  const handleSetActiveTab = (newValue) => {
    setActiveTab(newValue)
    if (onValueChange) {
      onValueChange(newValue)
    }
  }

  return (
    <TabsContext.Provider value={{ activeTab: value || activeTab, setActiveTab: handleSetActiveTab }}>
      <div className={className} {...props}>
        {children}
      </div>
    </TabsContext.Provider>
  )
}

export const TabsList = ({ children, className = '', ...props }) => {
  return (
    <div className={`flex space-x-2 bg-slate-900/90 backdrop-blur-xl p-2 rounded-xl border-2 border-slate-600/50 shadow-2xl ${className}`} {...props}>
      {children}
    </div>
  )
}

export const TabsTrigger = ({ children, value, className = '', ...props }) => {
  const { activeTab, setActiveTab } = useContext(TabsContext)
  const isActive = activeTab === value

  return (
    <button
      onClick={() => setActiveTab(value)}
      className={`flex-1 px-6 py-3 rounded-lg text-sm font-bold transition-all duration-300 transform ${
        isActive
          ? 'bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-white shadow-xl shadow-blue-500/40 scale-105 border-2 border-blue-400'
          : 'bg-slate-800/60 text-slate-400 hover:bg-slate-700/80 hover:text-white hover:scale-102 border-2 border-transparent'
      } ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}

export const TabsContent = ({ children, value, className = '', ...props }) => {
  const { activeTab } = useContext(TabsContext)

  if (activeTab !== value) return null

  return (
    <div className={`transition-opacity duration-300 ${className}`} {...props}>
      {children}
    </div>
  )
}
