---
name: animation-recipes
description: Receitas prontas de animacoes 60fps para landing pages usando Framer Motion, GSAP e CSS. Use quando precisar implementar scroll animations, parallax, micro-interactions e transicoes suaves.
allowed-tools:
  - Read
  - Write
  - Edit
---

# Animation Recipes

Receitas prontas de animacoes 60fps para landing pages modernas.

## Quick Start

1. Instale as dependencias: `npm install framer-motion gsap @studio-freight/lenis`
2. Configure o Lenis provider para smooth scroll
3. Escolha as receitas adequadas para cada secao
4. Sempre use transform e opacity (GPU accelerated)

## Setup Inicial

### Lenis Provider
```tsx
// providers/SmoothScroll.tsx
'use client';
import Lenis from '@studio-freight/lenis';
import { useEffect, useRef } from 'react';

export function SmoothScroll({ children }: { children: React.ReactNode }) {
  const lenisRef = useRef<Lenis | null>(null);

  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
    });

    lenisRef.current = lenis;

    function raf(time: number) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    return () => {
      lenis.destroy();
    };
  }, []);

  return <>{children}</>;
}
```

### GSAP Plugin Registration
```tsx
// lib/animations.ts
'use client';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

export { gsap, ScrollTrigger };
```

## Receitas Framer Motion

### Fade In Up (Entrada basica)
```tsx
import { motion } from 'framer-motion';

const fadeInUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] }
};

<motion.div {...fadeInUp}>
  Conteudo
</motion.div>
```

### Stagger Children (Itens em sequencia)
```tsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: 'easeOut' }
  }
};

<motion.ul variants={container} initial="hidden" animate="show">
  {items.map((i) => (
    <motion.li key={i} variants={item}>{i}</motion.li>
  ))}
</motion.ul>
```

### Scroll Reveal (Aparecer ao rolar)
```tsx
<motion.div
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, margin: '-100px' }}
  transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
>
  Conteudo
</motion.div>
```

### Hover Scale (Botao interativo)
```tsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={{ type: 'spring', stiffness: 400, damping: 17 }}
>
  Clique aqui
</motion.button>
```

### Card Hover 3D
```tsx
function Card3D({ children }) {
  const [rotateX, setRotateX] = useState(0);
  const [rotateY, setRotateY] = useState(0);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    setRotateX((y - centerY) / 10);
    setRotateY((centerX - x) / 10);
  };

  return (
    <motion.div
      onMouseMove={handleMouseMove}
      onMouseLeave={() => { setRotateX(0); setRotateY(0); }}
      style={{
        rotateX,
        rotateY,
        transformStyle: 'preserve-3d',
      }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      {children}
    </motion.div>
  );
}
```

## Receitas GSAP

### Scroll Reveal Basico
```tsx
useEffect(() => {
  const ctx = gsap.context(() => {
    gsap.fromTo(
      '.reveal',
      { opacity: 0, y: 50 },
      {
        opacity: 1,
        y: 0,
        duration: 1,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: '.reveal',
          start: 'top 80%',
          toggleActions: 'play none none reverse'
        }
      }
    );
  });

  return () => ctx.revert();
}, []);
```

### Parallax Background
```tsx
useEffect(() => {
  const ctx = gsap.context(() => {
    gsap.to('.parallax-bg', {
      yPercent: -30,
      ease: 'none',
      scrollTrigger: {
        trigger: '.parallax-section',
        start: 'top bottom',
        end: 'bottom top',
        scrub: true
      }
    });
  });

  return () => ctx.revert();
}, []);
```

### Text Split Animation
```tsx
useEffect(() => {
  const ctx = gsap.context(() => {
    const chars = gsap.utils.toArray('.split-char');

    gsap.fromTo(
      chars,
      { opacity: 0, y: 50 },
      {
        opacity: 1,
        y: 0,
        stagger: 0.03,
        duration: 0.5,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: '.split-text',
          start: 'top 80%',
        }
      }
    );
  });

  return () => ctx.revert();
}, []);
```

### Pin Section (Secao fixa)
```tsx
useEffect(() => {
  const ctx = gsap.context(() => {
    ScrollTrigger.create({
      trigger: '.pin-section',
      start: 'top top',
      end: '+=100%',
      pin: true,
      pinSpacing: true
    });
  });

  return () => ctx.revert();
}, []);
```

### Counter Animation
```tsx
useEffect(() => {
  const ctx = gsap.context(() => {
    gsap.to('.counter', {
      textContent: 1000,
      duration: 2,
      ease: 'power1.out',
      snap: { textContent: 1 },
      scrollTrigger: {
        trigger: '.counter',
        start: 'top 80%',
      }
    });
  });

  return () => ctx.revert();
}, []);
```

## Micro-interactions

### Magnetic Button
```tsx
function MagneticButton({ children }) {
  const buttonRef = useRef<HTMLButtonElement>(null);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!buttonRef.current) return;
    const { left, top, width, height } = buttonRef.current.getBoundingClientRect();
    const x = (e.clientX - left - width / 2) * 0.3;
    const y = (e.clientY - top - height / 2) * 0.3;
    buttonRef.current.style.transform = `translate(${x}px, ${y}px)`;
  };

  const handleMouseLeave = () => {
    if (!buttonRef.current) return;
    buttonRef.current.style.transform = 'translate(0, 0)';
  };

  return (
    <button
      ref={buttonRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="transition-transform duration-300 ease-out"
    >
      {children}
    </button>
  );
}
```

### Cursor Follower
```tsx
function CursorFollower() {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <motion.div
      className="fixed w-4 h-4 bg-primary rounded-full pointer-events-none z-50 mix-blend-difference"
      animate={{ x: position.x - 8, y: position.y - 8 }}
      transition={{ type: 'spring', stiffness: 500, damping: 28 }}
    />
  );
}
```

## Performance Tips

### Reduced Motion
```tsx
const prefersReducedMotion = typeof window !== 'undefined'
  ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
  : false;

const animation = prefersReducedMotion
  ? { opacity: 1 }
  : { opacity: 1, y: 0 };
```

### GPU Acceleration
```css
.animated-element {
  will-change: transform, opacity;
  transform: translateZ(0);
}
```

### Cleanup Pattern
```tsx
useEffect(() => {
  const ctx = gsap.context(() => {
    // animacoes aqui
  }, containerRef);

  return () => ctx.revert(); // SEMPRE fazer cleanup
}, []);
```
