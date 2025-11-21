import { HeroGeometric } from "@/components/ui/shape-landing-hero";
import { LiquidButton } from '@/components/ui/liquid-glass-button';
import Link from 'next/link';

export default function LandingPage() {
    return (
        <div className="relative">
            <HeroGeometric
                badge="Next Inai"
                title1="Build Stunning"
                title2="Websites with AI"
            />
            <div className="absolute bottom-20 left-0 right-0 flex justify-center z-20">
                <Link href="/builder">
                    <LiquidButton className="text-white border rounded-full" size={'xl'}>Start Building</LiquidButton>
                </Link>
            </div>
        </div>
    );
}
