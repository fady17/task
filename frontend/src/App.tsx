
import { DesktopLayout } from './layouts/DesktopLayout';
import { MobileLayout } from './layouts/MobileLayout';
// import { SessionProvider } from './context/SessionContext';

function App() {
  return (
   
      <div className="dark">
        <div className="md:hidden">
          <MobileLayout />
        </div>
        <div className="hidden md:block">
          <DesktopLayout />
        </div>
      </div>
    
  );
}

export default App;
