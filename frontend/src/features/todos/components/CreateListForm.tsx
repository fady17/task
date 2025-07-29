import { useState, type FormEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent} from '@/components/ui/card'; //, CardHeader, CardTitle 
import { Plus } from 'lucide-react';

interface CreateListFormProps {
  onAddList: (title: string) => void;
}

export function CreateListForm({ onAddList }: CreateListFormProps) {
  const [title, setTitle] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (title.trim() && !isLoading) {
      setIsLoading(true);
      try {
        await onAddList(title.trim());
        setTitle('');
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <Card className="border-2 border-neutral-800 bg-black shadow-2xl">
      {/* <CardHeader className="bg-white text-black rounded-t-lg">
        <CardTitle className="flex items-center gap-3 text-xl font-bold">
          <div className="w-10 h-10 bg-black rounded-xl flex items-center justify-center">
            <Plus className="w-5 h-5 text-white" />
          </div>
          Create New List
        </CardTitle>
      </CardHeader> */}
      <CardContent className="p-6">
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-4">
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter list title... (e.g., 'Weekend Plans', 'Work Tasks')"
            className="flex-1 h-12 text-lg border-2 bg-black border-neutral-700 focus:border-white transition-all duration-200 text-white placeholder:text-neutral-400 rounded-xl"
            disabled={isLoading}
            maxLength={100}
          />
          <Button
            type="submit"
            disabled={!title.trim() || isLoading}
            className="h-12 px-8 bg-white text-black hover:bg-neutral-200 transition-all duration-200 shadow-lg rounded-xl font-semibold whitespace-nowrap"
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-black border-t-transparent rounded-full animate-spin mr-2" />
                Creating...
              </>
            ) : (
              <>
                <Plus className="w-5 h-5 mr-2" />
                Create List
              </>
            )}
          </Button>
        </form>
        
        {/* Character count indicator */}
        <div className="mt-3 text-right">
          <span className={`text-xs ${title.length > 80 ? 'text-red-400' : 'text-neutral-500'}`}>
            {title.length}/100
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
