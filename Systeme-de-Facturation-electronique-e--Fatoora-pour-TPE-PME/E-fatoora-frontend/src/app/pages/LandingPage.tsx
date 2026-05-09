import React from 'react';
import { motion } from 'framer-motion';
import { Link } from "react-router";

import { 
  ChevronRight, 
  BarChart3, 
  ShieldCheck, 
  Zap, 
  CheckCircle2, 
  ArrowRight,
  PlayCircle
} from 'lucide-react';

const LandingPage: React.FC = () => {
  // Liste des utilisateurs pour le carousel (Style Swiver)
  const users = [
    { name: "Carthago Dev", icon: "CD" },
    { name: "Digital Solutions", icon: "DS" },
    { name: "Alpha Consulting", icon: "AC" },
    { name: "Smart Finance", icon: "SF" },
    { name: "Global Trade", icon: "GT" },
    { name: "Tech Vision", icon: "TV" },
  ];

  const scrollingUsers = [...users, ...users];

  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans selection:bg-purple-100 selection:text-purple-700">
      
      {/* --- NAVBAR --- */}
      <nav className="flex items-center justify-between px-6 md:px-20 py-5 bg-white/80 backdrop-blur-md sticky top-0 z-50 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <img src="/src/styles/logo.png" alt="E-Fatoora" className="h-10 w-auto" />
          <span className="text-2xl font-black tracking-tight text-slate-900">
            E-FATOORA<span className="text-purple-600">.</span>
          </span>
        </div>

        <div className="hidden lg:flex gap-10 text-[13px] font-bold uppercase tracking-wider text-slate-500">
          <a href="#" className="hover:text-purple-600 transition-colors">Produits</a>
          <a href="#" className="hover:text-purple-600 transition-colors">Fonctionnalités</a>
          <a href="#" className="hover:text-purple-600 transition-colors">Tarifs</a>
        </div>

        <div className="flex items-center gap-4">
        <Link
        to="/login"
        className="hidden sm:block text-[13px] font-bold uppercase tracking-wider text-slate-900 px-4 py-2 hover:bg-slate-50 rounded-lg transition-all"
             >
           Connexion
          </Link>          
          <button className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-full text-[12px] font-black uppercase tracking-widest shadow-lg shadow-purple-200 transition-all active:scale-95">
            Essai Gratuit
          </button>
        </div>
      </nav>

      {/* --- HERO SECTION (Style Swiver) --- */}
      <section className="pt-20 pb-12 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-5xl md:text-7xl font-black text-slate-900 mb-8 leading-[1.1] tracking-tight">
              Gérez votre facturation <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-slate-400">en toute simplicité.</span>
            </h1>
            <p className="text-xl text-slate-500 mb-10 max-w-2xl mx-auto leading-relaxed">
              La plateforme tout-en-un pour créer des factures, suivre vos paiements et automatiser votre comptabilité selon les normes Tunisienne.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
              <button className="flex items-center gap-2 bg-slate-900 text-white px-8 py-5 rounded-2xl font-bold text-lg hover:bg-purple-600 transition-all shadow-xl shadow-slate-200">
                Commencer maintenant <ChevronRight size={20} />
              </button>
              <button className="flex items-center gap-2 px-8 py-5 rounded-2xl font-bold text-lg border border-slate-200 hover:bg-slate-50 transition-all text-slate-600">
                <PlayCircle size={20} /> Voir la démo
              </button>
            </div>
          </motion.div>

          {/* Image du Dashboard Mockup (Comme swiver.io) */}
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.8 }}
            className="relative max-w-5xl mx-auto rounded-3xl border border-slate-200 shadow-[0_40px_100px_-20px_rgba(0,0,0,0.1)] overflow-hidden bg-slate-50"
          >
            <div className="bg-white border-b border-slate-200 px-4 py-3 flex gap-2">
              <div className="w-3 h-3 rounded-full bg-red-400"></div>
              <div className="w-3 h-3 rounded-full bg-amber-400"></div>
              <div className="w-3 h-3 rounded-full bg-emerald-400"></div>
            </div>
            <img 
              src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=2426&auto=format&fit=crop" 
              alt="Dashboard Preview" 
              className="w-full h-auto object-cover opacity-90"
            />
          </motion.div>
        </div>
      </section>

      {/* --- CAROUSEL UTILISATEURS (Défilement Continu) --- */}
      <div className="py-24 bg-slate-50/50 border-y border-slate-100 overflow-hidden">
        <p className="text-center text-[11px] font-black uppercase tracking-[0.3em] text-slate-400 mb-12">
          Plus de 10,000 entreprises nous font confiance
        </p>
        <div className="relative flex">
          <motion.div 
            className="flex gap-12 whitespace-nowrap"
            animate={{ x: [0, -1000] }}
            transition={{ repeat: Infinity, duration: 30, ease: "linear" }}
          >
            {scrollingUsers.map((user, idx) => (
              <div key={idx} className="flex items-center gap-4 grayscale opacity-60 hover:grayscale-0 hover:opacity-100 transition-all cursor-default">
                <div className="w-12 h-12 rounded-xl bg-purple-600 flex items-center justify-center text-white font-black">
                  {user.icon}
                </div>
                <span className="text-xl font-bold text-slate-700 tracking-tight">{user.name}</span>
              </div>
            ))}
          </motion.div>
        </div>
      </div>

      {/* --- FEATURES GRID --- */}
      <section className="py-32 px-6 max-w-7xl mx-auto">
        <div className="text-center mb-20">
          <h2 className="text-[12px] font-black uppercase tracking-[0.3em] text-purple-600 mb-4">Pourquoi choisir E-Fatoora ?</h2>
          <p className="text-4xl font-black text-slate-900 tracking-tight">Tout ce dont vous avez besoin <br/> pour propulser votre business.</p>
        </div>

        <div className="grid md:grid-cols-3 gap-12">
          {[
            { icon: <Zap />, title: "Rapide & Intuitif", desc: "Créez vos documents commerciaux en quelques clics seulement." },
            { icon: <ShieldCheck />, title: "100% Conforme", desc: "Une solution agréée respectant les normes fiscales de votre région." },
            { icon: <BarChart3 />, title: "Analytique", desc: "Visualisez votre santé financière avec des graphiques clairs." }
          ].map((item, i) => (
            <div key={i} className="group p-8 rounded-3xl border border-slate-100 hover:border-purple-200 hover:bg-purple-50/30 transition-all duration-300">
              <div className="mb-6 w-14 h-14 bg-slate-900 text-white rounded-2xl flex items-center justify-center group-hover:bg-purple-600 transition-colors">
                {item.icon}
              </div>
              <h3 className="text-xl font-black mb-4 text-slate-900">{item.title}</h3>
              <p className="text-slate-500 leading-relaxed font-medium">{item.desc}</p>
              <div className="mt-6 flex items-center gap-2 text-purple-600 font-bold text-sm cursor-pointer">
                En savoir plus <ArrowRight size={16} />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* --- SECTION STATS --- */}
      <section className="py-24 bg-slate-900 text-white rounded-[3rem] mx-6 mb-24 overflow-hidden relative">
        <div className="absolute top-0 right-0 w-64 h-64 bg-purple-600/20 blur-[100px]"></div>
        <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-12 text-center relative z-10">
          <div>
            <div className="text-5xl font-black mb-2 tracking-tighter">98%</div>
            <div className="text-slate-400 text-sm font-bold uppercase tracking-widest">Satisfaction Client</div>
          </div>
          <div>
            <div className="text-5xl font-black mb-2 tracking-tighter">24h/7</div>
            <div className="text-slate-400 text-sm font-bold uppercase tracking-widest">Support Technique</div>
          </div>
          <div>
            <div className="text-5xl font-black mb-2 tracking-tighter">+500k</div>
            <div className="text-slate-400 text-sm font-bold uppercase tracking-widest">Factures Générées</div>
          </div>
        </div>
      </section>

      {/* --- FOOTER --- */}
      <footer className="py-20 border-t border-slate-100 bg-slate-50/30 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="flex items-center gap-3">
             <span className="text-xl font-black tracking-tight text-slate-900">E-FATOORA<span className="text-purple-600">.</span></span>
          </div>
          <div className="text-slate-400 text-sm font-medium">
            © 2024 E-Fatoora. Tous droits réservés. Inspiré par l'excellence.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;