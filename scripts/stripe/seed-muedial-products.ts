import Stripe from 'stripe';
import { config } from 'dotenv';

/**
 * MUEDial Stripe Product & Price Seed Script
 *
 * Creates the following products and prices on Stripe:
 *
 * Subscriptions (recurring monthly):
 *   1. MUEDial Basic  — $19.99/month (1,000 credits)
 *   2. MUEDial Pro    — $34.99/month (1,700 credits)
 *   3. MUEDial Studio — $49.99/month (3,000 credits)
 *
 * One-time purchases:
 *   4. MUEDial Credit Pack Small — $12.99 (500 credits)
 *   5. MUEDial Credit Pack Large — $34.99 (1,500 credits)
 *
 * Usage:
 *   STRIPE_SECRET_KEY=sk_test_... npx tsx scripts/stripe/seed-muedial-products.ts
 *   or set STRIPE_SECRET_KEY in .env.local and run: npx tsx scripts/stripe/seed-muedial-products.ts
 *
 * Options:
 *   --dry-run    Print what would be created without calling Stripe API
 */

config({ path: '.env.local' });

const DRY_RUN = process.argv.includes('--dry-run');

if (!process.env.STRIPE_SECRET_KEY) {
  console.error('STRIPE_SECRET_KEY is required. Set it in .env.local or pass as env var.');
  process.exit(1);
}

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

type PlanConfig = {
  name: string;
  description: string;
  priceUsd: number; // in dollars (e.g. 19.99)
  recurring: boolean;
  metadata: Record<string, string>;
};

const plans: PlanConfig[] = [
  // --- Subscriptions ---
  {
    name: 'MUEDial Basic',
    description: 'Monthly subscription with 1,000 credits',
    priceUsd: 19.99,
    recurring: true,
    metadata: {
      tier: 'basic',
      credits: '1000',
      type: 'subscription',
    },
  },
  {
    name: 'MUEDial Pro',
    description: 'Monthly subscription with 1,700 credits',
    priceUsd: 34.99,
    recurring: true,
    metadata: {
      tier: 'pro',
      credits: '1700',
      type: 'subscription',
    },
  },
  {
    name: 'MUEDial Studio',
    description: 'Monthly subscription with 3,000 credits',
    priceUsd: 49.99,
    recurring: true,
    metadata: {
      tier: 'studio',
      credits: '3000',
      type: 'subscription',
    },
  },
  // --- One-time Credit Packs ---
  {
    name: 'MUEDial Credit Pack Small',
    description: 'One-time purchase of 500 credits',
    priceUsd: 12.99,
    recurring: false,
    metadata: {
      tier: 'credit_pack_small',
      credits: '500',
      type: 'one_time',
    },
  },
  {
    name: 'MUEDial Credit Pack Large',
    description: 'One-time purchase of 1,500 credits',
    priceUsd: 34.99,
    recurring: false,
    metadata: {
      tier: 'credit_pack_large',
      credits: '1500',
      type: 'one_time',
    },
  },
];

async function seedProducts() {
  console.log(DRY_RUN ? '--- DRY RUN ---\n' : '');
  console.log(`Creating ${plans.length} products on Stripe...\n`);

  const envLines: string[] = [];

  for (const plan of plans) {
    const amountCents = Math.round(plan.priceUsd * 100);
    const label = plan.recurring ? `$${plan.priceUsd}/month` : `$${plan.priceUsd} (one-time)`;

    console.log(`  ${plan.name} — ${label}`);

    if (DRY_RUN) {
      console.log(`    [dry-run] Would create product + price (${amountCents} cents USD)\n`);
      continue;
    }

    const product = await stripe.products.create({
      name: plan.name,
      description: plan.description,
      metadata: plan.metadata,
    });

    const priceParams: Stripe.PriceCreateParams = {
      product: product.id,
      unit_amount: amountCents,
      currency: 'usd',
      metadata: plan.metadata,
    };

    if (plan.recurring) {
      priceParams.recurring = { interval: 'month' };
    }

    const price = await stripe.prices.create(priceParams);

    console.log(`    Product: ${product.id}`);
    console.log(`    Price:   ${price.id}\n`);

    const envKey = `STRIPE_PRICE_${plan.metadata.tier.toUpperCase()}`;
    envLines.push(`${envKey}=${price.id}`);
  }

  if (!DRY_RUN && envLines.length > 0) {
    console.log('--- Add to .env.local ---');
    for (const line of envLines) {
      console.log(line);
    }
  }

  console.log('\nDone.');
}

seedProducts()
  .then(() => process.exit(0))
  .catch((err) => {
    console.error('Failed:', err);
    process.exit(1);
  });
