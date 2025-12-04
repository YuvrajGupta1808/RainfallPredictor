import { Cloud, CloudRain, Sun, CloudSun, Droplets } from 'lucide-react';
import { cn } from '@/lib/utils';

interface WeatherIconProps {
  type: 'cloud' | 'rain' | 'sun' | 'cloudsun' | 'droplets';
  className?: string;
  size?: number;
}

export const WeatherIcon = ({ type, className, size = 48 }: WeatherIconProps) => {
  const icons = {
    cloud: Cloud,
    rain: CloudRain,
    sun: Sun,
    cloudsun: CloudSun,
    droplets: Droplets,
  };

  const Icon = icons[type];

  return (
    <Icon
      size={size}
      className={cn('text-primary/60', className)}
    />
  );
};
