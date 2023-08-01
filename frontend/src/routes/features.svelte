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
      <h1 class="text-4xl font-bold mb-4">Features</h1>
      <h2 class="text-3xl mb-2">User Dashboard</h2>
      <p class="text-lg text-white mb-6">
        This is the main page for users where they can see an overview of all their projects and quickly create a new one.
      </p>
      <h2 class="text-3xl mb-2">Project Overview</h2>
      <p class="text-lg text-white mb-6">
        This is where users can manipulate sections and see a gallery of uploaded and synthesized files for each project.
      </p>
      <h2 class="text-3xl mb-2">Voice Cloning & Creation</h2>
      <p class="text-lg text-white mb-6">
        Users can create a unique voice by uploading voice samples. The page shows previously uploaded samples and the status of the synthesized voice.
      </p>
      <h2 class="text-3xl mb-2">Voice Library</h2>
      <p class="text-lg text-white">
        This page shows all available voices. Users can listen to a sample of each voice.
      </p>
    </div>
  </div>
  