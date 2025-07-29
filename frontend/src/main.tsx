import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
// import { AppProvider } from './context/AppContext.tsx'
import { SessionProvider } from './context/SessionContext.tsx'
// import { ConnectionProvider } from './context/ConnectionContext.tsx'
// import { ConfigProvider } from './context/ConfigContext.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
       
       
       <SessionProvider>
      <App />
    </SessionProvider>
    


  </StrictMode>,
)
