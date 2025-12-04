import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';

const Index = () => {
  const navigate = useNavigate();


  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden bg-gradient-to-br from-blue-50 via-sky-50 to-cyan-50">
      {/* Gradient Mesh Blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Top left blob */}
        <div 
          className="absolute -top-32 -left-32 w-96 h-96 rounded-full opacity-60 blur-3xl animate-float"
          style={{ background: 'radial-gradient(circle, hsl(200 80% 80%) 0%, transparent 70%)' }}
        />
        {/* Top right blob */}
        <div 
          className="absolute -top-20 right-0 w-80 h-80 rounded-full opacity-50 blur-3xl animate-float-delayed"
          style={{ background: 'radial-gradient(circle, hsl(210 70% 85%) 0%, transparent 70%)' }}
        />
        {/* Center blob */}
        <div 
          className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full opacity-40 blur-3xl"
          style={{ background: 'radial-gradient(circle, hsl(195 75% 75%) 0%, transparent 70%)' }}
        />
        {/* Bottom left blob */}
        <div 
          className="absolute bottom-0 -left-20 w-72 h-72 rounded-full opacity-50 blur-3xl animate-float-delayed"
          style={{ background: 'radial-gradient(circle, hsl(205 85% 82%) 0%, transparent 70%)' }}
        />
        {/* Bottom right blob */}
        <div 
          className="absolute -bottom-20 right-10 w-96 h-96 rounded-full opacity-45 blur-3xl animate-float"
          style={{ background: 'radial-gradient(circle, hsl(190 70% 78%) 0%, transparent 70%)' }}
        />
        {/* Extra accent blob */}
        <div 
          className="absolute top-1/2 right-1/4 w-64 h-64 rounded-full opacity-35 blur-3xl animate-float"
          style={{ background: 'radial-gradient(circle, hsl(215 80% 88%) 0%, transparent 70%)' }}
        />
      </div>


      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-4 relative z-10">
        <div className="text-center max-w-2xl mx-auto animate-fade-in">
          {/* Title */}
          <h1 className="text-5xl md:text-7xl font-bold text-foreground mb-6 tracking-tight">
            Rainfall Predictor
          </h1>

          {/* Subtitle */}
          <p className="text-xl text-muted-foreground mb-12 max-w-md mx-auto leading-relaxed">
            Get accurate rainfall predictions for major cities around the world.
          </p>

          {/* CTA Button */}
          <Button
            onClick={() => navigate('/chat')}
            variant="hero"
            size="xl"
            className="group"
          >
            Start Chat
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Button>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-6 text-center text-sm text-muted-foreground relative z-10">
        <p>Powered by intelligent weather analysis</p>
      </footer>
    </div>
  );
};

export default Index;
