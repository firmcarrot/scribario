import { Hero } from "@/components/sections/Hero";
import { Proof } from "@/components/sections/Proof";
import { HowItWorks } from "@/components/sections/HowItWorks";
import { Demo } from "@/components/sections/Demo";
import { FinalCTA } from "@/components/sections/FinalCTA";
import { Footer } from "@/components/sections/Footer";

export default function Home() {
  return (
    <main id="main-content">
      <Hero />
      <Proof />
      <HowItWorks />
      <Demo />
      <FinalCTA />
      <Footer />
    </main>
  );
}
