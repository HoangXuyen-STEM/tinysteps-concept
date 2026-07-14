# Integration Test Plan: Double-Submit Prevention

To verify that the `complete_lesson_rpc` properly prevents a race condition when two requests attempt to submit a lesson simultaneously, perform the following integration test against a live Supabase instance.

## Context
If a user rapidly double-clicks the submit button, or a network retry causes two identical payload submissions to arrive at the server concurrently, we must ensure that:
1. `lesson_progress` correctly UPSERTs without throwing a unique constraint violation.
2. `daily_activity.lessons_completed` only increments by **1** (not 2).

## Setup
1. Apply migrations `000001_init_user_state.sql` and `000002_complete_lesson_rpc.sql` to your Supabase project.
2. Create a test user and obtain a valid `access_token`.
3. Choose a lesson ID, e.g., `starters_lesson_001`.
4. Ensure the user's `lesson_progress` for this lesson is either missing or `not_started`.

## Test Execution

Execute a script that fires two concurrent calls to the RPC. You can use a simple Node.js script:

```javascript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient('YOUR_SUPABASE_URL', 'YOUR_SUPABASE_ANON_KEY', {
  global: {
    headers: { Authorization: `Bearer YOUR_USER_ACCESS_TOKEN` }
  }
});

async function runConcurrentTest() {
  const lessonId = 'starters_lesson_001';
  const score = 100;

  console.log('Sending two concurrent requests...');
  
  // Fire both requests at the exact same time
  const results = await Promise.allSettled([
    supabase.rpc('complete_lesson_rpc', { p_lesson_id: lessonId, p_score: score }),
    supabase.rpc('complete_lesson_rpc', { p_lesson_id: lessonId, p_score: score })
  ]);
  
  console.log(results);
}

runConcurrentTest();
```

## Expected Verification Results

1. Both promises should resolve successfully without throwing errors (no 500 status).
2. Query the `lesson_progress` table:
   ```sql
   SELECT score, status FROM lesson_progress WHERE user_id = '...' AND lesson_id = 'starters_lesson_001';
   ```
   **Expected:** 1 row, `status = 'completed'`, `score = 100`.
3. Query the `daily_activity` table:
   ```sql
   SELECT lessons_completed FROM daily_activity WHERE user_id = '...';
   ```
   **Expected:** `lessons_completed` must be exactly **1** (or +1 from the previous count). If it incremented by 2, the advisory lock failed.

## Why this works
The migration uses `pg_advisory_xact_lock(hashtext(v_user_id::text), hashtext(p_lesson_id))` to force Postgres to serialize the two transactions. The second transaction will wait at the lock until the first commits. When it proceeds, it re-evaluates `v_old_status` against the committed data of the first transaction, sees it is now `'completed'`, and skips the `daily_activity` insertion block.
