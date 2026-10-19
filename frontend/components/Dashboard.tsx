'use client';

import { useCallback, useState } from 'react';
import { DashboardProvider } from '@/lib/dashboard-store';
import type { TabId } from '@/lib/types';
import DemoModal from './DemoModal';
import Footer from './Footer';
import Header from './Header';
import Sidebar from './Sidebar';
import Benchmarks from './tabs/Benchmarks';
import HitlQueue from './tabs/HitlQueue';
import Overview from './tabs/Overview';
import PolicyFeed from './tabs/PolicyFeed';
import SwarmTopology from './tabs/SwarmTopology';

export default function Dashboard() {
  const [tab, setTab] = useState<TabId>('overview');
  const [demoOpen, setDemoOpen] = useState(false);
  const openDemo = useCallback(() => setDemoOpen(true), []);
  const closeDemo = useCallback(() => setDemoOpen(false), []);

  return (
    <DashboardProvider>
      <Header active={tab} onTabChange={setTab} onOpenDemo={openDemo} />

      <div className="flex flex-1 gap-6 px-4 sm:px-6 lg:px-8 pb-8 pt-2 w-full max-w-[1600px] mx-auto">
        <Sidebar active={tab} onChange={setTab} />
        <main className="flex-1 min-w-0 space-y-6">
          {tab === 'overview' && <Overview />}
          {tab === 'policy' && <PolicyFeed onOpenDemo={openDemo} />}
          {tab === 'swarm' && <SwarmTopology />}
          {tab === 'benchmarks' && <Benchmarks onOpenDemo={openDemo} />}
          {tab === 'hitl' && <HitlQueue />}
        </main>
      </div>

      <Footer />
      <DemoModal open={demoOpen} onClose={closeDemo} />
    </DashboardProvider>
  );
}
