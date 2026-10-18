'use client';

import { useCallback, useState } from 'react';
import { DashboardProvider } from '@/lib/dashboard-store';
import type { TabId } from '@/lib/types';
import DemoModal from './DemoModal';
import Footer from './Footer';
import Header from './Header';
import TabNav from './TabNav';
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
      <Header onOpenDemo={openDemo} />
      <TabNav active={tab} onChange={setTab} />

      <main className="flex-1 px-6 lg:px-10 py-8 max-w-7xl mx-auto w-full space-y-10">
        {tab === 'overview' && <Overview />}
        {tab === 'policy' && <PolicyFeed onOpenDemo={openDemo} />}
        {tab === 'swarm' && <SwarmTopology />}
        {tab === 'benchmarks' && <Benchmarks onOpenDemo={openDemo} />}
        {tab === 'hitl' && <HitlQueue />}
      </main>

      <Footer />
      <DemoModal open={demoOpen} onClose={closeDemo} />
    </DashboardProvider>
  );
}
