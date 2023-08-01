<script>
    import { goto } from '$app/navigation';
  </script>
  
  <div class="container mx-auto px-4">
    <nav class="flex justify-between py-6">
      <ul class="flex items-center">
        <li>
          <button class="text-xl font-bold text-white" on:click={() => goto('/')}>Scriptorium</button>
        </li>
        <li class="ml-6">
          <button class="text-lg text-white" on:click={() => goto('/auth')}>Login/Signup</button>
        </li>
        <!-- Add more navigation links here -->
      </ul>
    </nav>
  
    <div class="mt-10">
      <h1 class="text-4xl font-bold mb-4">Welcome to Scriptorium</h1>
      <p class="text-lg text-white">
        Scriptorium is a web-based application specifically designed for authors, particularly those who are self-published or associated with smaller publishing houses that may lack extensive resources for in-house audiobook production.
      </p>
      <!-- More content here -->
    </div>
  </div>
  