/**
 * @file example.js
 * @description Demonstrates how to initialize the Apina JavaScript SDK and call sample endpoints.
 *
 * @features
 * - Initializes an ApinaClient against a local registry URL
 * - Exercises representative DexScreener and Meteora requests
 * - Logs request outcomes for manual verification
 */
import { ApinaClient } from './dist/index.js';

async function main() {
  console.log('Initializing ApinaClient...');
  const apina = new ApinaClient({ registryUrl: 'http://localhost:8000' });

  try {
    await apina.init();
    console.log('ApinaClient initialized successfully!');
  } catch (error) {
    console.error('Initialization failed:', error);
    return;
  }

  // Test Case 1: DexScreener (no parameters)
  try {
    console.log('\n--- Testing DexScreener: Get Latest Token Profiles (No params) ---');
    const profiles = await apina.dexscreener.getTokenProfilesLatestV1();
    console.log('Response type:', typeof profiles);
    console.log('Is array:', Array.isArray(profiles));
    console.log('Response sample:', JSON.stringify(profiles).substring(0, 300) + '...');
  } catch (error) {
    console.error('DexScreener Latest Token Profiles test failed:', error.message);
  }

  // Test Case 2: DexScreener (Path parameter)
  try {
    console.log('\n--- Testing DexScreener: Get Meta Info (Path parameter: slug) ---');
    const metaData = await apina.dexscreener.getMetasMetaV1Slug({ slug: 'solana' });
    console.log('Response type:', typeof metaData);
    console.log('Response sample:', JSON.stringify(metaData).substring(0, 300) + '...');
  } catch (error) {
    console.error('DexScreener Meta Info test failed (expected 500 if endpoint is down):', error.message);
  }

  // Test Case 3: Meteora DLMM (Query parameter: page_size)
  try {
    console.log('\n--- Testing Meteora: Get DLMM Pools (Query parameter: page_size) ---');
    const pools = await apina.meteora.getPools({ page_size: 2 });
    console.log('Response type:', typeof pools);
    console.log('Is array:', Array.isArray(pools));
    console.log('Page size returned:', pools.page_size);
    console.log('Data length:', pools.data ? pools.data.length : 'N/A');
    console.log('Response sample:', JSON.stringify(pools).substring(0, 300) + '...');
  } catch (error) {
    console.error('Meteora DLMM Pools test failed:', error.message);
  }
}

main();
