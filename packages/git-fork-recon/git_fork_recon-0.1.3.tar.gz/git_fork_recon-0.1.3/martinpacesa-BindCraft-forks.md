# Fork Analysis Report for martinpacesa/BindCraft

Repository: [martinpacesa/BindCraft](https://github.com/martinpacesa/BindCraft)

Description: User friendly and accurate binder design pipeline

Stars: 583

## Fork Analysis

Found 34 active forks with significant changes.


### [mjb84/BindCraft](https://github.com/mjb84/BindCraft)

**Stats:**
- Commits ahead: 61
- Commits behind: 20
- Stars: 0

- Pull Requests:


- Last updated: 2025-05-27T12:22:57+00:00

**Summary of Changes:**
This fork primarily focuses on **enhancing the installation process and introducing new configuration options for protein design, particularly for multimeric systems**.

The main themes are:
1.  **Improved and diversified installation scripts**: Significant effort has been put into making the installation more robust and offering alternatives (e.g., without Conda, with specific CUDA versions).
2.  **Expanded protein design configuration**: A new default 3-stage multimer design setting has been added, and existing multimer design settings have been subtly updated, likely tuning parameters for better performance or specific use cases.

**Significant new features or improvements:**
*   **New `install_cuda.sh` script**: This is a major addition aimed at simplifying CUDA installation, which is often a dependency headache for GPU-accelerated applications. It includes logic for different CUDA versions and driver installations.
*   **New `install_noconda.sh` script**: Provides an alternative installation path for users who prefer not to use Conda, increasing flexibility.
*   **Refined `install_bindcraft.sh`**: Updates to the main installation script suggest a more streamlined or robust setup process, possibly addressing previous installation issues.
*   **New `default_3stage_multimer.json` configuration**: This introduces a new default setting for 3-stage multimer design, providing a ready-to-use configuration for a specific design strategy. This includes parameters for design algorithm, sampling, weights for various loss functions (plddt, pae, contacts, helicity, i-ptm, rg, termini distance), MPNN settings, and saving options.

**Notable code refactoring or architectural changes:**
*   The numerous small changes across existing `settings_advanced/*.json` files indicate a fine-tuning of existing multimer design parameters. While individually small (3 insertions, 3 deletions), collectively they suggest an iterative optimization process, likely adjusting specific weights or iteration counts for different multimer design scenarios (e.g., "flexible", "hardtarget", "mpnn", "betasheet"). The changes are predominantly in `num_seqs`, `backbone_noise`, and `sampling_temp` values, suggesting adjustments to the sequence sampling and backbone perturbation during design.

**Potential impact or value of the changes:**
*   **Increased Accessibility**: The improved installation scripts (especially for CUDA and the non-Conda option) will significantly lower the barrier to entry for new users and make setting up the environment much smoother on various systems.
*   **Enhanced Design Capabilities**: The new 3-stage multimer design configuration provides a new tool for users, and the adjustments to existing configurations suggest ongoing optimization and refinement of the protein design algorithms, potentially leading to better design outcomes for specific protein types or design goals.
*   **Improved Reproducibility**: Providing well-defined, version-controlled JSON settings for different design strategies helps ensure reproducibility of results.

**Tags:**
*   installation
*   feature
*   functionality
*   improvement

**Commits:**

- [46a2d3fe](/commit/46a2d3fe3da69f01f01ed27f3dcd27c73f54ee10) - <span style="color:green">+67</span>/<span style="color:red">-0</span> (1 files): Create default_3stage_multimer.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [8c35c407](/commit/8c35c40757b31f7d776ccd850b6add812755cecd) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update peptide_3stage_multimer_mpnn_flexible.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [ff647a61](/commit/ff647a61cf685713ce3c49a0d43a79cc383b7721) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update peptide_3stage_multimer_mpnn.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [91a84952](/commit/91a8495246d4e16306f4349daccd97ae4ba06373) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update peptide_3stage_multimer_flexible.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [d5ad728e](/commit/d5ad728e5b72e5635e856cecccf9a14427371dfd) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update default_4stage_multimer_mpnn_hardtarget.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [748835d3](/commit/748835d3a25c5071dc6ac609a875685f0c9caf2b) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update default_4stage_multimer_mpnn_flexible_hardtarget.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [391316fd](/commit/391316fddc8b32e061da95c47324f9c7d2db224c) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update default_4stage_multimer_mpnn_flexible.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [86f42cac](/commit/86f42cac477fcc19f9de8b6223c9e12938d71611) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update default_4stage_multimer_flexible_hardtarget.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [d1e238fd](/commit/d1e238fdc79dda13476060d367fc36aa7e0ded41) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update default_4stage_multimer_flexible.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [3ca44d85](/commit/3ca44d850add822471006a60a2b82fe77e3e4d7b) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update betasheet_4stage_multimer_mpnn_hardtarget.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [d708b25f](/commit/d708b25f67abf96a610e7e6ab5a7e8f7d20c1423) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update betasheet_4stage_multimer_mpnn_flexible_hardtarget.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [cb36d004](/commit/cb36d004511767bacf2c910f052177a22aa28e97) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update betasheet_4stage_multimer_mpnn_flexible.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [d80278bd](/commit/d80278bd423b0592ec451c5f9255dab2776ba0fd) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update default_4stage_multimer_hardtarget.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [5a5b1f38](/commit/5a5b1f380a29b340a0e12138e8deb14046ed54db) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update betasheet_4stage_multimer_hardtarget.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [0c276489](/commit/0c27648937ad73b923cbcb95dcc7dd1aa29b44b5) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update betasheet_4stage_multimer_flexible_hardtarget.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [b23f0d30](/commit/b23f0d30af9ece6c035d584892e4aad326d41099) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update betasheet_4stage_multimer_flexible.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [e0afc41b](/commit/e0afc41b856fd930b7d711da6123e90111ecf302) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update peptide_3stage_multimer.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [1a0a259e](/commit/1a0a259e29fee8eefce8b715a91322356aa58677) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update default_4stage_multimer_mpnn.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [81fabdd6](/commit/81fabdd636f518429aa37bf93c24bc09db067355) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update default_4stage_multimer.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [f7960a9e](/commit/f7960a9e450ffc56a922e357eeca0c7611ea797a) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update betasheet_4stage_multimer_mpnn.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [d509aab8](/commit/d509aab8c3ad3f8e425d4f504c507b85f7ddb7f1) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update betasheet_4stage_multimer.json [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [aaae4ccc](/commit/aaae4cccdc7b9e68458cf100add129ed5bcfb118) - <span style="color:green">+26</span>/<span style="color:red">-11</span> (1 files): Update install_cuda.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [36da792b](/commit/36da792bd9be8d63b03fbe697783a642bf1fa787) - <span style="color:green">+7</span>/<span style="color:red">-0</span> (1 files): Update install_cuda.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [e50545fe](/commit/e50545feebb27225f27a02e4d40074056e917d0d) - <span style="color:green">+25</span>/<span style="color:red">-15</span> (1 files): Update install_cuda.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [c7d09408](/commit/c7d094084c17a7a0e5ef0e27f6dfc8835769a0b4) - <span style="color:green">+154</span>/<span style="color:red">-0</span> (1 files): Create install_cuda.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [c2723885](/commit/c2723885bc299d41ee7116011733e3e3f0f04fca) - <span style="color:green">+1</span>/<span style="color:red">-1</span> (1 files): Update install_bindcraft.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [5cf61694](/commit/5cf61694cc1e9764d21afdbe0560cec81db1e935) - <span style="color:green">+99</span>/<span style="color:red">-171</span> (1 files): Update install_bindcraft.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [84abaf3c](/commit/84abaf3ce88036b54307bfaac4f9da6a9ee3f6c2) - <span style="color:green">+118</span>/<span style="color:red">-61</span> (1 files): Update install_bindcraft.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [f34c8730](/commit/f34c87306d4b0120ae9945c9261e816bdd8fc21d) - <span style="color:green">+5</span>/<span style="color:red">-0</span> (1 files): Update install_bindcraft.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [d6c933da](/commit/d6c933daa819c4c26ffa516d824d53c01eeaadd2) - <span style="color:green">+23</span>/<span style="color:red">-45</span> (1 files): Update install_bindcraft.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [fc1b2c1f](/commit/fc1b2c1f196aceb6ff7dbe4572a9c80fe3e5b181) - <span style="color:green">+4</span>/<span style="color:red">-0</span> (1 files): Update install_noconda.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [57db4dcf](/commit/57db4dcfa79d84417fe219348dd46407e2889ee8) - <span style="color:green">+3</span>/<span style="color:red">-7</span> (1 files): Update install_noconda.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [591a4bec](/commit/591a4bec44dee473c8847562c092a3c7028e27d2) - <span style="color:green">+4</span>/<span style="color:red">-0</span> (1 files): Update install_noconda.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [75bdf726](/commit/75bdf726323952acb536d63973f6e0aadf334884) - <span style="color:green">+200</span>/<span style="color:red">-0</span> (1 files): Create install_noconda.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [da74f9a7](/commit/da74f9a7ad322fb542b3bac0d1d692a7fe833928) - <span style="color:green">+16</span>/<span style="color:red">-15</span> (1 files): Update install_bindcraft.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [1a48ce48](/commit/1a48ce48762ca4dad6d27b506f6d245bd5625489) - <span style="color:green">+1</span>/<span style="color:red">-0</span> (1 files): Update install_bindcraft.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [ff53d42a](/commit/ff53d42a0cacf7e119056f632f149b19cabab477) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): Update install_bindcraft.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]

- [94f0f20c](/commit/94f0f20c6195a2caf20b55b5b6d8d190d52fe551) - <span style="color:green">+15</span>/<span style="color:red">-9</span> (1 files): Update install_bindcraft.sh [mjb84 <155462087+mjb84@users.noreply.github.com>]


---

### [alpha29/BindCraft_mess](https://github.com/alpha29/BindCraft_mess)

**Stats:**
- Commits ahead: 37
- Commits behind: 37
- Stars: 0

- Pull Requests:


- Last updated: 2025-05-14T17:52:24+00:00

**Summary of Changes:**
The primary purpose of this fork is to significantly refactor and modernize the `bindcraft` project, transitioning it from a collection of scripts into a structured Python package with improved dependency management, code quality, and user experience.

Here's a breakdown of the key changes and their impact:

**Main Themes:**

*   **Project Structuring and Packaging:** The project is being reorganized into a proper Python package (`bindcraft`) with submodules for functions and command-line interface. This improves maintainability, reusability, and discoverability of components.
*   **Modern Dependency Management:** Migration from ad-hoc dependency handling to `Poetry` for dependency management, ensuring reproducible builds and easier installation.
*   **Code Quality and Formatting:** Integration of `black`, `isort`, and `ruff` for automated code formatting and linting, enforcing consistent code style and catching potential issues early.
*   **Enhanced Logging:** Introduction of `loguru` for more robust and configurable logging, replacing basic `print` statements. This includes file-based logging and better log organization.
*   **CLI Development:** Implementation of a command-line interface (CLI) using `typer` (implied by `root.py` usage and `adds cli` commit message), making the tool more user-friendly and scriptable.
*   **Google Colab Compatibility:** Adjustments to accommodate running the project within Google Colab environments, including handling AlphaFold parameter downloads and file system layout.

**Significant New Features or Improvements:**

*   **Structured CLI:** The introduction of a `bindcraft` CLI via `bindcraft/cmd/root.py` makes the application more accessible and provides a standardized way to interact with its functionalities.
*   **Improved Logging:** The switch to `loguru` offers better control over log output, including file logging and customizable formats, which is crucial for debugging and monitoring long-running processes.
*   **Dependency Management with Poetry:** This is a major improvement for development and deployment, ensuring that all required packages are correctly installed and versioned.
*   **Support for Colab Environment:** Explicitly addressing the needs of a Colab environment (e.g., parameter downloads) extends the usability of the tool to cloud-based computational platforms.
*   **Inclusion of `polars` and `ipython`:** These additions suggest an intent to improve data manipulation capabilities and interactive development/debugging experience.
*   **New Data and Configuration:** Addition of an `EGFR.json` config file and an `EGFR` PDB file (`6aru_final_chain_A_domain_3.pdb`) indicates the setup for specific use cases or examples.

**Notable Code Refactoring or Architectural Changes:**

*   **Module Restructuring:** Moving functions from a flat `functions/` directory into `bindcraft/functions/` and the main script `bindcraft.py` into `bindcraft/runner.py` significantly improves the project's modularity and adherence to standard Python package structure.
*   **Explicit `data/in` and `data/out` directories:** Standardizing input and output data locations.
*   **Extensive `.gitignore` updates:** Reflecting the new project structure, build artifacts, and sensitive data/parameters, improving repository cleanliness.
*   **`print` statements replaced with `logger.info`:** A fundamental shift towards a more professional and debuggable logging approach.

**Potential Impact or Value of the Changes:**

*   **Increased Maintainability:** The structured project layout, automated formatting, and clear dependency management will make the codebase easier to understand, maintain, and contribute to.
*   **Enhanced User Experience:** The CLI and improved logging will make the tool more user-friendly and provide better feedback during execution.
*   **Broader Accessibility:** Colab compatibility opens up the tool to users who might not have local computational resources or prefer cloud environments.
*   **Improved Reproducibility:** Poetry ensures that environments can be replicated consistently, reducing "works on my machine" issues.
*   **Foundation for Future Development:** The refactoring lays a solid architectural foundation for adding new features and expanding the project's capabilities.

**Tags:**

*   installation
*   feature
*   functionality
*   improvement
*   ui
*   refactor
*   documentation (via README updates and .gitignore for docs/build)

**Commits:**

- [525650a4](/commit/525650a411216332e6a77c5320ada513cc72d86e) - <span style="color:green">+7</span>/<span style="color:red">-2</span> (2 files): sort this out someday [cbrown <vanguard737@gmail.com>]

- [8a7c6cd0](/commit/8a7c6cd0bfb1fd234f2732ef7689a654c4110923) - <span style="color:green">+2</span>/<span style="color:red">-1</span> (2 files): logging directory [cbrown <vanguard737@gmail.com>]

- [52a91a76](/commit/52a91a76b6931a36a0b6f8d71001a3589eaf755c) - <span style="color:green">+1</span>/<span style="color:red">-0</span> (1 files): gitignores out/ [cbrown <vanguard737@gmail.com>]

- [4102d8b9](/commit/4102d8b907188eb3c06e87ad71295260a26d41dd) - <span style="color:green">+285</span>/<span style="color:red">-1</span> (2 files): adds ipython and polars [cbrown <vanguard737@gmail.com>]

- [404ee06e](/commit/404ee06ed7e1dc1b8048d790ba19027720bc118e) - <span style="color:green">+80</span>/<span style="color:red">-64</span> (7 files): black/isort/ruff [cbrown <vanguard737@gmail.com>]

- [1401ab15](/commit/1401ab150eeb3cf661431233ea336539833c7682) - <span style="color:green">+2</span>/<span style="color:red">-0</span> (1 files): gitignore params/ [cbrown <vanguard737@gmail.com>]

- [ac466d1b](/commit/ac466d1bc0ebf85fea70b04a02ed5039998704e9) - <span style="color:green">+2</span>/<span style="color:red">-2</span> (1 files): better settings [cbrown <vanguard737@gmail.com>]

- [63af6c5c](/commit/63af6c5cee5bb012c2d152180b9d2fe1754e0b18) - <span style="color:green">+1327</span>/<span style="color:red">-0</span> (1 files): adds EGFR pdb [cbrown <vanguard737@gmail.com>]

- [042aad33](/commit/042aad331736270e112263883259ec33e6c2022a) - <span style="color:green">+234</span>/<span style="color:red">-3</span> (5 files): accommodate running at colab too (downloading af params, tweaks to fs layout) [cbrown <vanguard737@gmail.com>]

- [4887fccb](/commit/4887fccb246a94c7787636550dcbc1f673991102) - <span style="color:green">+0</span>/<span style="color:red">-0</span> (2 files): adds data/in and data/out directories [cbrown <vanguard737@gmail.com>]

- [2f437a87](/commit/2f437a87d855916de155c1a8ba8f9b28de8a1c5f) - <span style="color:green">+1</span>/<span style="color:red">-1</span> (1 files): ah jeez [cbrown <vanguard737@gmail.com>]

- [686711fb](/commit/686711fb048759620ea462c39e65f020642f578b) - <span style="color:green">+89</span>/<span style="color:red">-1</span> (2 files): adds deps [cbrown <vanguard737@gmail.com>]

- [7e8d05ee](/commit/7e8d05eebaf17dc1c856a62349af4bc533b3004b) - <span style="color:green">+31</span>/<span style="color:red">-29</span> (2 files): print -> logger.info [cbrown <vanguard737@gmail.com>]

- [beeb414f](/commit/beeb414f3efa07eb785c7d3af02a51e6d3dc0a63) - <span style="color:green">+205</span>/<span style="color:red">-24</span> (2 files): jax[cuda] dep [cbrown <vanguard737@gmail.com>]

- [4305c438](/commit/4305c438404d17fb332751e8720757c8a896595e) - <span style="color:green">+1</span>/<span style="color:red">-1</span> (1 files): hmm, not sure how this ever worked elsewhere... [cbrown <vanguard737@gmail.com>]

- [e5837f78](/commit/e5837f78c479ca7d08b3da50cbe853730f0bf0dc) - <span style="color:green">+4</span>/<span style="color:red">-0</span> (1 files): gitignore logfile [cbrown <vanguard737@gmail.com>]

- [d35a699f](/commit/d35a699f4861ce4b2819324361f9891b08be6f48) - <span style="color:green">+2</span>/<span style="color:red">-2</span> (1 files): ugh [cbrown <vanguard737@gmail.com>]

- [d2420c7f](/commit/d2420c7f2ec62c4609eb7074dedddc593dd275ed) - <span style="color:green">+1</span>/<span style="color:red">-1</span> (1 files): logfile formatting [cbrown <vanguard737@gmail.com>]

- [d6d3f801](/commit/d6d3f8011f4d6d5dedf2aa5659f08350a2062458) - <span style="color:green">+5</span>/<span style="color:red">-17</span> (3 files): oops [cbrown <vanguard737@gmail.com>]

- [1a33a938](/commit/1a33a93840270e8d22a630a622aa45b8c2c843af) - <span style="color:green">+9</span>/<span style="color:red">-3</span> (1 files): wip [cbrown <vanguard737@gmail.com>]

- [bbcaf0a3](/commit/bbcaf0a3f1cb7164707a1a021d8a15cb1914bbb7) - <span style="color:green">+1</span>/<span style="color:red">-0</span> (1 files): test out file logging [cbrown <vanguard737@gmail.com>]

- [65f41497](/commit/65f414972a828b71bf71a8ac6d0cd23b8a729d11) - <span style="color:green">+15</span>/<span style="color:red">-0</span> (1 files): CLI [cbrown <vanguard737@gmail.com>]

- [ed317835](/commit/ed317835a35fcc3639ceba0fc9f7dde3ab34f0a6) - <span style="color:green">+9</span>/<span style="color:red">-0</span> (1 files): config file for EGFR [cbrown <vanguard737@gmail.com>]

- [e812d88f](/commit/e812d88f885ed8cc2da930ce669f34c4db6bce6e) - <span style="color:green">+1059</span>/<span style="color:red">-1056</span> (2 files): renaming [cbrown <vanguard737@gmail.com>]

- [0ad9f41d](/commit/0ad9f41dfd21336c37a8b1c100649a70c107e0eb) - <span style="color:green">+131</span>/<span style="color:red">-2</span> (5 files): adds cli [cbrown <vanguard737@gmail.com>]

- [f6fe5180](/commit/f6fe5180bdc2e8cf18451347eeff7dd38c5cf8ff) - <span style="color:green">+249</span>/<span style="color:red">-80</span> (4 files): adds loguru [cbrown <vanguard737@gmail.com>]

- [04f4ce02](/commit/04f4ce025222ec82cd656b88439521bcd7b9368d) - <span style="color:green">+13</span>/<span style="color:red">-1</span> (2 files): adds pyrosettacolabsetup dep [cbrown <vanguard737@gmail.com>]

- [b17d582b](/commit/b17d582b9360dd1d264f823cacd5f13a217a0074) - <span style="color:green">+1</span>/<span style="color:red">-1</span> (1 files): black/isort/ruff (~no changes, upstream must have done this already) [cbrown <vanguard737@gmail.com>]

- [b76299be](/commit/b76299be3d134171ed8a023bed95bde3d2651865) - <span style="color:green">+970</span>/<span style="color:red">-0</span> (1 files): wrapper [cbrown <vanguard737@gmail.com>]

- [34882a45](/commit/34882a45b8aa289ae1189cfce031df65441786a6) - <span style="color:green">+815</span>/<span style="color:red">-815</span> (2 files): bindcraft.py -> scripts/ [cbrown <vanguard737@gmail.com>]

- [0b5cb580](/commit/0b5cb580a5a386fac4408e609f4a669ed1c94719) - <span style="color:green">+1874</span>/<span style="color:red">-1874</span> (11 files): move functions into bindcraft module [cbrown <vanguard737@gmail.com>]

- [37133c50](/commit/37133c504aeacfac63b41dc1c299c7d8867dbffa) - <span style="color:green">+0</span>/<span style="color:red">-0</span> (4 files): move third-party executables to bin/ [cbrown <vanguard737@gmail.com>]

- [a965e5a3](/commit/a965e5a3e72495d79c868a003187648225c2fdf3) - <span style="color:green">+1375</span>/<span style="color:red">-495</span> (6 files): black/isort/ruff [cbrown <vanguard737@gmail.com>]

- [38397dcf](/commit/38397dcf57343cd0e475de4ef4fe301344b0d33a) - <span style="color:green">+167</span>/<span style="color:red">-1</span> (2 files): Adds black/isort/ruff dependencies. [cbrown <vanguard737@gmail.com>]

- [070a7378](/commit/070a73787f3a713b2965a231313b20ee2ea8df61) - <span style="color:green">+1312</span>/<span style="color:red">-0</span> (2 files): Adds poetry and dependencies. [cbrown <vanguard737@gmail.com>]

- [afeb1ba9](/commit/afeb1ba913595e57bf09e949caf76e43d16794d0) - <span style="color:green">+68</span>/<span style="color:red">-0</span> (1 files): Adds .gitignore. [cbrown <vanguard737@gmail.com>]


---

### [SuperChrisW/BindCraft](https://github.com/SuperChrisW/BindCraft)

**Stats:**
- Commits ahead: 19
- Commits behind: 0
- Stars: 1

- Pull Requests:


- Last updated: 2025-07-01T14:03:11+00:00

**Summary of Changes:**
This fork of the BindCraft repository introduces significant enhancements focused on improving protein design capabilities, particularly through the integration of MPNN (Message Passing Neural Network) and FastRelax protocols, and a more modular codebase.

### **Summary of Changes and Innovations:**

The main themes of these changes revolve around:

1.  **Enhanced Protein Sequence Design:** A primary focus is on integrating MPNN-based sequence design, allowing for more intelligent and robust binder design by leveraging MPNN's ability to generate sequences based on structural context. This includes pre-filtering and scoring designs using MPNN.
2.  **Improved Structural Refinement and Scoring:** The "FastRelax" protocol is introduced, likely for structural optimization post-design, and a new `pTMEnergy` metric replaces `iptm` loss, suggesting a shift towards more accurate or application-specific energy evaluations for predicted structures.
3.  **Modularization and Code Organization:** The codebase has undergone significant refactoring to be more modular, making it easier to maintain, extend, and integrate new functionalities. This includes reorganizing files into `extra_functions` and `settings_advanced` directories.
4.  **Flexible Pipeline Configuration:** New JSON settings files provide extensive configuration options for different design pipelines, including various multimer stages, flexible designs, and hard target constraints, often with dedicated MPNN variants.

### **Significant New Features or Improvements:**

*   **MPNN-FR Pipeline:** A major new feature is the implementation of an "MPNN-FastRelax" pipeline. This suggests a workflow where MPNN generates sequences, and then a FastRelax step refines the resulting protein structures, potentially leading to higher quality designs.
*   **MPNN-Based Scoring and Filtering:** The addition of `bindcraft_mpnnScore.py` and associated functionalities allows for pre-filtering and ranking of binder backbone designs based on MPNN scores, enabling the selection of more promising candidates early in the design process.
*   **Sequence Design Scoring:** A new "pipeline sequence design scoring" is added, likely to evaluate the quality of newly designed sequences.
*   **`pTMEnergy` Implementation:** The replacement of `iptm` loss with `pTMEnergy` indicates a new or refined energy metric for evaluating protein models, potentially leading to more accurate predictions of protein stability and binding.
*   **Advanced Settings for Multimer Design:** Numerous new JSON settings files (e.g., `betasheet_4stage_multimer_mpnn.json`, `default_4stage_multimer_flexible_hardtarget.json`) offer highly granular control over multimer design, including options for different stages, flexibility, and hard targets, now with MPNN-specific configurations.
*   **Quality Checks:** Integration of quality checks within the MPNN-FR pipeline.

### **Notable Code Refactoring or Architectural Changes:**

*   **Modularization:** The `bindcraft_module.py` file becomes central, indicating a shift from monolithic scripts to a more modular, function-based design. Old filter logic was also removed, suggesting a streamlining of the filtering process.
*   **File Structure Reorganization:** Files are moved into `extra_functions` and `settings_advanced` directories, improving code organization and separation of concerns. `extra_functions` now contains patch files for external libraries (Biopython, ColabDesign, ProteinMPNN), indicating a strategy to extend or modify their behavior without directly altering original source code.
*   **Removal of `bindcraft_Filters.py` and `bindcraft_module.py` refactoring:** The deletion of `bindcraft_Filters.py` and significant changes to `bindcraft_module.py` suggest a consolidation or re-implementation of filtering logic within the main module or other specialized functions.

### **Potential Impact or Value of the Changes:**

These changes are likely to significantly enhance the capabilities of BindCraft for protein design. The integration of MPNN and FastRelax could lead to:

*   **Higher Quality Designs:** MPNN's ability to generate realistic sequences and FastRelax's structural refinement can produce more stable and functional protein binders.
*   **Improved Efficiency:** MPNN-based pre-filtering can help prune less promising designs early, saving computational resources.
*   **Greater Flexibility:** The extensive new settings files offer unprecedented control over the design process, allowing users to tailor pipelines to specific research needs (e.g., designing flexible multimers or targeting specific binding sites).
*   **Easier Maintenance and Extension:** The modular refactoring makes the codebase more approachable for future development and contributions.

### **Tags:**

*   feature
*   functionality
*   refactor
*   improvement
*   documentation (implied by new settings files and potentially updated usage)

**Commits:**

- [6d40c528](/commit/6d40c528e6ec96bda5e6327bebf8f564b71d4db3) - <span style="color:green">+25</span>/<span style="color:red">-22</span> (19 files): Merge branch 'martinpacesa:main' into main [WANG LIYAO <liyao-wang@qq.com>]

- [e097bae8](/commit/e097bae8e4b1731e67df50e941ec6bf187131f72) - <span style="color:green">+0</span>/<span style="color:red">-72</span> (1 files): delete Filter [SuperChrisW <liyao-wang@qq.com>]

- [59ad5ccd](/commit/59ad5ccdc1d440d6d436902ae46c7e88c4fbf86e) - <span style="color:green">+727</span>/<span style="color:red">-301</span> (3 files): add pipeline sequencce design scoring [SuperChrisW <liyao-wang@qq.com>]

- [e5445be3](/commit/e5445be37f9491f41e0e1807286b27e4f8547174) - <span style="color:green">+1411</span>/<span style="color:red">-0</span> (2 files): update settings for MPNN-FR pipeline [SuperChrisW <liyao-wang@qq.com>]

- [e8eb4b6d](/commit/e8eb4b6d6ae44ba858a6ce5c584373babcc85f57) - <span style="color:green">+368</span>/<span style="color:red">-20</span> (2 files): revise mpnn-FR pipeline& add quality check [SuperChrisW <liyao-wang@qq.com>]

- [9271ecc5](/commit/9271ecc5cb9181e490513fcb6521bcf2e0d821cb) - <span style="color:green">+170</span>/<span style="color:red">-53</span> (2 files): implement mpnn-fastrelax pipeline [SuperChrisW <liyao-wang@qq.com>]

- [b48cf11a](/commit/b48cf11a4c79887b6613dd09f1710ae64c88bb24) - <span style="color:green">+2746</span>/<span style="color:red">-1999</span> (19 files): re-organize file structure [SuperChrisW <liyao-wang@qq.com>]

- [d8c034f1](/commit/d8c034f1a3462cb77e4cea124ea6c49c13b2f560) - <span style="color:green">+236</span>/<span style="color:red">-0</span> (1 files): revise hotspot_residues func [SuperChrisW <liyao-wang@qq.com>]

- [17c483f0](/commit/17c483f05893a791220577c77fdbdbd34f001871) - <span style="color:green">+6</span>/<span style="color:red">-1</span> (1 files): update [SuperChrisW <liyao-wang@qq.com>]

- [a7447ff4](/commit/a7447ff407c42c40da693331aedecef446de3b8c) - <span style="color:green">+37</span>/<span style="color:red">-9</span> (1 files): script for Backbone rank by mpnn score [SuperChrisW <liyao-wang@qq.com>]

- [67fc95e4](/commit/67fc95e4a4b6b60ed105d19c85a62b3e43c9272b) - <span style="color:green">+239</span>/<span style="color:red">-0</span> (1 files): prefilter binder backbone design by mpnn score [SuperChrisW <liyao-wang@qq.com>]

- [27ef0dde](/commit/27ef0ddeebdd6ae41876ab6855fef4c1104a580d) - <span style="color:green">+5</span>/<span style="color:red">-9</span> (1 files): Merge branch 'main' of github.com:SuperChrisW/BindCraft into main [SuperChrisW <liyao-wang@qq.com>]

- [9072e8c4](/commit/9072e8c4c1472e784ff3d1846a74d0d7ad6c99e6) - <span style="color:green">+508</span>/<span style="color:red">-3</span> (5 files): add script start from mpnn opt [SuperChrisW <liyao-wang@qq.com>]

- [f7c7f7e3](/commit/f7c7f7e356b04fb9bf45644ef4ad2fb380a922f1) - <span style="color:green">+5</span>/<span style="color:red">-9</span> (1 files): Merge branch 'martinpacesa:main' into main [WANG LIYAO <liyao-wang@qq.com>]

- [bc84a63c](/commit/bc84a63c207a8009433d3b7216a75f5d9a0d2d20) - <span style="color:green">+35</span>/<span style="color:red">-33</span> (1 files): rewrite bindcraft script to module based [SuperChrisW <liyao-wang@qq.com>]

- [07c98d60](/commit/07c98d6064ebe05eb3b6749e58b99cf921ab58f5) - <span style="color:green">+794</span>/<span style="color:red">-551</span> (5 files): rewrite bindcraft script to modules [SuperChrisW <liyao-wang@qq.com>]

- [e3062481](/commit/e3062481aeabaf7264616d03662a591fc5819732) - <span style="color:green">+1318</span>/<span style="color:red">-0</span> (3 files): add modifed codes for simple replacing [SuperChrisW <liyao-wang@qq.com>]

- [23bb2fb5](/commit/23bb2fb5d6a8d0d21dfa65db334193576390304c) - <span style="color:green">+1428</span>/<span style="color:red">-0</span> (4 files): update settings for pTME loss [SuperChrisW <liyao-wang@qq.com>]

- [fbfdd3ce](/commit/fbfdd3ceb3185b8cce0ee58406782dc027c7af1a) - <span style="color:green">+641</span>/<span style="color:red">-0</span> (3 files): implement pTMEnergy instead of iptm loss [SuperChrisW <liyao-wang@qq.com>]


---

### [fabianackle/BindCraft](https://github.com/fabianackle/BindCraft)

**Stats:**
- Commits ahead: 9
- Commits behind: 13
- Stars: 0

- Pull Requests:


- Last updated: 2025-04-06T12:54:59+00:00

**Summary of Changes:**
This fork introduces several key changes primarily focused on improving the **deployment, execution, and example data** for a project likely related to protein binding/design (given the name "BindCraft").

**Main Themes:**

*   **Improved Environment Management and Installation:** The fork introduces a `conda` environment file (`BindCraft.yml`) and updates related installation scripts, making the setup process more robust and reproducible.
*   **Cluster Integration (SLURM):** Significant effort has been put into adapting the project to run on SLURM-managed high-performance computing clusters, specifically mentioning the "s3it uzh cluster." This indicates a move towards scalable computation.
*   **New Example Data and Settings:** A new example target, "LOOP" (a sybody), is added with its corresponding PDB file and settings, providing a concrete use case or benchmark.

**Significant New Features or Improvements:**

*   **Conda Environment:** The `BindCraft.yml` file provides a comprehensive and reproducible environment definition, simplifying dependency management and installation. This is a major improvement for usability and reliability.
*   **SLURM Scripting:** The `bindcraft.slurm` script has been adapted for cluster submission, including path adjustments and cluster-specific configurations. This enables running BindCraft jobs on HPC systems.
*   **New "LOOP" Example:** The addition of `LOOP.pdb` and `LOOP.json` provides a new, concrete example for users to test or understand the functionality, particularly for sybody-related tasks.
*   **`.gitignore`:** The addition of a `.gitignore` file helps maintain a clean repository by excluding unwanted files (e.g., build artifacts, temporary files).

**Notable Code Refactoring or Architectural Changes:**

*   While no direct code refactoring of the core application logic is evident in these commits, the changes to environment management and SLURM scripts represent significant architectural improvements for deployment and execution.
*   The merging of `martinpacesa:main` into `main` (commit `[af600cee](https://github.com/martinpacesa/BindCraft/commit/af600cee)`) suggests a previous merge where various advanced settings for multimer and peptide design were introduced or refined. Although the details of *those* changes aren't in this diff, their presence indicates an expanded scope of design capabilities.

**Potential Impact or Value:**

*   **Easier Adoption:** The `conda` environment significantly lowers the barrier to entry for new users, making the project easier to install and run.
*   **Scalability:** SLURM integration enables researchers to run large-scale computational experiments, which is crucial for demanding tasks like protein design or high-throughput screening.
*   **Clearer Examples:** The new example provides a tangible demonstration of BindCraft's capabilities, especially for sybody design, which can aid in understanding and application.
*   **Improved Collaboration:** A proper environment definition and `.gitignore` contribute to a more professional and collaborative development workflow.

---

**Tags:**

*   installation
*   feature (new example target)
*   functionality (SLURM integration for execution)
*   improvement (environment management, SLURM script adjustments)
*   documentation (implied by `README.md` changes, though not detailed in diff)
*   refactor (changes to installation process, not core application logic)

**Commits:**

- [62a51803](/commit/62a51803bfe71695570be72309a268542aa489f8) - <span style="color:green">+1</span>/<span style="color:red">-1</span> (1 files): Updated BindCraft environment. [Fabian Ackle <fabian.ackle@gmail.com>]

- [7256d84a](/commit/7256d84ac196041a2cdf089a1b2afe66c95ba076) - <span style="color:green">+2</span>/<span style="color:red">-5</span> (1 files): Adjusted path for bindcraft.py in slurm script. [Fabian Ackle <fabian.ackle@gmail.com>]

- [217d8900](/commit/217d890038bbe24b4a761155069d11011a153edf) - <span style="color:green">+9</span>/<span style="color:red">-0</span> (1 files): Added setting for LOOP. [Fabian Ackle <fabian.ackle@gmail.com>]

- [508751ce](/commit/508751ce3843507825d5d98cede751698b58f750) - <span style="color:green">+913</span>/<span style="color:red">-0</span> (1 files): Added loop example sybody as target. [Fabian Ackle <fabian.ackle@gmail.com>]

- [e6a604c2](/commit/e6a604c2ec187f955f1654a97a817171da2826cf) - <span style="color:green">+9</span>/<span style="color:red">-11</span> (1 files): Adjusted slurm script for s3it uzh cluster. [Fabian Ackle <fabian.ackle@gmail.com>]

- [affc92d4](/commit/affc92d4acfd30eca7d62711ae07d530f84ba9cd) - <span style="color:green">+1</span>/<span style="color:red">-0</span> (1 files): Added gitignore [Fabian Ackle <fabian.ackle@gmail.com>]

- [3307eab5](/commit/3307eab583516c597bfbd440b6db20fdb9d6a074) - <span style="color:green">+1</span>/<span style="color:red">-1</span> (1 files): Update BindCraft.yml [Fabian Ackle <38766976+fabianackle@users.noreply.github.com>]

- [af600cee](/commit/af600cee4bff1f5427f515e453d0198ba5d20f7a) - <span style="color:green">+30</span>/<span style="color:red">-50</span> (25 files): Merge branch 'martinpacesa:main' into main [Fabian Ackle <38766976+fabianackle@users.noreply.github.com>]

- [a0b5e80d](/commit/a0b5e80db79bc1fb2b075acc334acafcdfbd3fe6) - <span style="color:green">+40</span>/<span style="color:red">-67</span> (3 files): Added BindCraft environment yml. [Fabian Ackle <fabian.ackle@gmail.com>]


---

### [czl368/BindCraft](https://github.com/czl368/BindCraft)

**Stats:**
- Commits ahead: 7
- Commits behind: 29
- Stars: 0

- Pull Requests:


- Last updated: 2024-12-11T18:54:40+00:00

**Summary of Changes:**
This fork primarily focuses on **streamlining and improving the installation process** for the BindCraft project, specifically by transitioning from a Conda-based environment setup to a **virtual environment (venv) approach**. It also includes updates to a Jupyter notebook and minor configuration changes.

### Main Themes and Innovations:

1.  **Virtual Environment Adoption**: The core change is the introduction of `install_bindcraft_venv.sh`, a new script that sets up BindCraft within a Python virtual environment. This offers several benefits:
    *   **Isolation**: Prevents dependency conflicts with other Python projects on the system.
    *   **Portability**: Makes it easier to manage and replicate the exact environment.
    *   **Reduced Overhead**: Eliminates the need for a full Conda installation and its associated overhead.
    *   **Cleaner Setup**: The script handles module loading (e.g., `python/3.10`, `scipy-stack`, `openmm`, `cudacore`, `cudnn`), virtual environment creation, package installation via `pip`, and even PyRosetta installation.

2.  **PyRosetta Integration**: The installation script now explicitly includes steps to download, extract, and install PyRosetta, which is a significant dependency for structural biology applications.

3.  **Dependency Management Refinement**: The `pip freeze --local > requirements.txt` command is used to capture the exact versions of installed packages, which is good practice for environment reproducibility.

4.  **Colab Notebook Path Fix**: A merged pull request addresses a path issue within the `BindCraft.ipynb` Colab notebook, improving its functionality.

### Significant New Features or Improvements:

*   **Simplified Installation**: The new `install_bindcraft_venv.sh` script provides a more direct and potentially less error-prone way to set up the BindCraft environment compared to the previous (presumably Conda-based) method.
*   **Explicit PyRosetta Installation**: Direct integration of PyRosetta installation into the setup script.
*   **Git Ignore Addition**: A `.gitignore` file is added, which is crucial for preventing unnecessary files (like environment directories or temporary files) from being committed to the repository.

### Notable Code Refactoring or Architectural Changes:

*   **Shift from Conda to Venv**: This is the most significant architectural change, moving away from a Conda-centric environment management to a more lightweight virtual environment.
*   **Centralized Installation Logic**: The `install_bindcraft_venv.sh` script centralizes almost all environment setup logic.
*   **Removal of Conda Cleanup Code**: Reflecting the shift, previous Conda cleanup logic is removed from the installation script.

### Potential Impact or Value of the Changes:

*   **Improved Developer Experience**: Easier and more reliable setup for new contributors or users, reducing friction.
*   **Enhanced Reproducibility**: Virtual environments and the `requirements.txt` file contribute to a more reproducible development and deployment environment.
*   **Resource Efficiency**: Virtual environments are generally lighter than full Conda environments.
*   **Better Project Hygiene**: The `.gitignore` file helps maintain a cleaner repository.

---

### Tags:

*   installation
*   feature (new venv installation script)
*   functionality (improved installation)
*   refactor (transition from conda to venv setup)
*   documentation (implicit improvement through clearer installation instructions in script)
*   improvement (easier setup, better environment management)

**Commits:**

- [872520ed](/commit/872520ed7218f8fe0a40846e266dec9b316f9843) - <span style="color:green">+15</span>/<span style="color:red">-5</span> (2 files): changed path for example json [Christina Li <christinali368@gmail.com>]

- [21ffe13e](/commit/21ffe13e33ec70a218da8457a4b0c5dadd722bec) - <span style="color:green">+6</span>/<span style="color:red">-56</span> (1 files): removed conda clearnup code [Christina Li <christinali368@gmail.com>]

- [646901cb](/commit/646901cbbfcfebfb06c6849be1acf41ed79a45c7) - <span style="color:green">+21</span>/<span style="color:red">-16</span> (1 files): installing pyrosetta [Christina Li <christinali368@gmail.com>]

- [6d50d9fa](/commit/6d50d9fa0711adccf8a9ebead8df287871789da8) - <span style="color:green">+586</span>/<span style="color:red">-14</span> (2 files): Add git ignore + intial venv changes [Christina Li <christinali368@gmail.com>]

- [90a6f4d3](/commit/90a6f4d320354fabbf0c4b84e732df1d285f78b7) - <span style="color:green">+120</span>/<span style="color:red">-0</span> (1 files): adding file to install venv [czl368 <christinali368@gmail.com>]

- [ff87229f](/commit/ff87229f53fa88d3623b5d928ed13b5c268abdb1) - <span style="color:green">+0</span>/<span style="color:red">-0</span> (1 files): testing [czl368 <christinali368@gmail.com>]

- [c5052887](/commit/c5052887a3ef9cec4d0ea4e1e8d7b23ed0943b89) - <span style="color:green">+879</span>/<span style="color:red">-878</span> (1 files): Merge pull request #1 from martinpacesa/main [Christina Li <108580250+czl368@users.noreply.github.com>]


---

### [alessandronascimento/BindCraft](https://github.com/alessandronascimento/BindCraft)

**Stats:**
- Commits ahead: 6
- Commits behind: 5
- Stars: 0

- Pull Requests:


- Last updated: 2025-06-26T21:52:27+00:00

**Summary of Changes:**
This fork introduces new features and improvements primarily focused on protein design, particularly for cyclic peptides and multimeric structures, by extending the `colabdesign` functionality.

### Main Themes and Innovations:

1.  **Enhanced Protein Design Capabilities**: The core of these changes revolves around adding more sophisticated options for designing proteins, especially cyclic peptides and multimeric complexes. This is evident through the introduction of a new advanced settings file and modifications to the design utility functions.
2.  **Flexible Design Workflow**: The new `cyclic_peptide_2stage_multimer_flexible.json` settings file suggests a more configurable and flexible approach to design, allowing users to fine-tune various parameters related to multimer design, sampling, and loss functions.
3.  **"Design an Existing Binder" Feature**: A significant new feature is the initial implementation for designing an existing binder, which could be very useful for optimizing or modifying pre-existing protein-ligand interactions.

### Significant New Features or Improvements:

*   **New Advanced Design Settings**: Introduction of `settings_advanced/cyclic_peptide_2stage_multimer_flexible.json` which specifies detailed parameters for a "2-stage multimer flexible" design algorithm. This includes:
    *   `use_multimer_design`: Explicitly enables multimer design.
    *   `design_algorithm`: Set to "2stage", indicating a multi-step design process.
    *   Various weights for different loss functions (`plddt`, `pae_intra`, `pae_inter`, `con_intra`, `con_inter`, `helicity`, `iptm`, `rg`, `termini_loss`), allowing for fine-grained control over the design objectives.
    *   Parameters for `MPNN` (Message Passing Neural Network) integration, including `mpnn_fix_interface` and `mpnn_weights`.
    *   Options for saving design animations and trajectory plots.
*   **"Design an Existing Binder" Functionality**: The `colabdesign_utils.py` file now includes an initial code block to support designing an existing binder, likely allowing users to input a known binder and then use the design algorithm to refine or alter it.
*   **Bug Fixes and Refinements in `colabdesign_utils.py`**: Several commits address minor bugs and corrections in the `prep_inputs` function and other parts of `colabdesign_utils.py`, improving the robustness and correctness of the design process.
*   **Control over Amino Acid Omission**: The `cyclic_peptide_2stage_multimer_flexible.json` includes `omit_AAs` and `force_reject_AA` settings, providing direct control over which amino acids can be used in the design.

### Notable Code Refactoring or Architectural Changes:

*   **Centralized Advanced Settings**: The introduction of a dedicated JSON file for advanced settings (`cyclic_peptide_2stage_multimer_flexible.json`) promotes a more organized and configurable approach to managing design parameters, moving them out of direct code and into a structured data format.
*   **Modularity in `colabdesign_utils.py`**: While not a drastic refactor, the additions and corrections within `colabdesign_utils.py` suggest an ongoing effort to compartmentalize different design functionalities.

### Potential Impact or Value of the Changes:

These changes significantly enhance the flexibility and power of the protein design tool.
The detailed control over design parameters and the explicit support for multimer and cyclic peptide design make it more versatile for researchers working on complex protein structures.
The "design an existing binder" feature opens up new avenues for optimizing pre-existing designs, which is crucial in drug discovery and protein engineering.
The bug fixes contribute to the overall stability and reliability of the software.

### Tags:

*   feature
*   functionality
*   bugfix
*   improvement
*   refactor

**Commits:**

- [7fa3a100](/commit/7fa3a10091e97fa06604bfe4b794d39e38054a0f) - <span style="color:green">+1</span>/<span style="color:red">-1</span> (1 files): Update cyclic_peptide_2stage_multimer_flexible.json [Alessandro Nascimento <al.s.nascimento@gmail.com>]

- [aed05720](/commit/aed057200bfd9f1851d34d28d42913998523623c) - <span style="color:green">+1</span>/<span style="color:red">-1</span> (1 files): Updated settings [alessandronascimento <al.s.nascimento@gmail.com>]

- [ec7d6faa](/commit/ec7d6faae43e9ee6d9b5d6ccb052e34b25c44b42) - <span style="color:green">+68</span>/<span style="color:red">-1</span> (2 files): Updating advanced settings [alessandronascimento <al.s.nascimento@gmail.com>]

- [e7bd0646](/commit/e7bd0646f17488b039085b8faea46f4bc9bf9328) - <span style="color:green">+5</span>/<span style="color:red">-6</span> (1 files): Update colabdesign_utils.py [Alessandro Nascimento <al.s.nascimento@gmail.com>]

- [ad0708ba](/commit/ad0708bafafbae3305ccfff874924f0d6750a7ef) - <span style="color:green">+1</span>/<span style="color:red">-1</span> (1 files): Update colabdesign_utils.py [Alessandro Nascimento <al.s.nascimento@gmail.com>]

- [487a8cea](/commit/487a8cea9b8ef0c4f6ac840f6ad03f6a6adbdd2c) - <span style="color:green">+46</span>/<span style="color:red">-3</span> (1 files): Update colabdesign_utils.py [Alessandro Nascimento <al.s.nascimento@gmail.com>]


---

### [skadaba1/BindCraft](https://github.com/skadaba1/BindCraft)

**Stats:**
- Commits ahead: 6
- Commits behind: 29
- Stars: 0

- Pull Requests:


- Last updated: 2024-12-05T09:12:01+00:00

**Summary of Changes:**
The changes in this fork primarily focus on enhancing the `colabdesign_utils.py` module, which appears to be central to a protein binder design pipeline. The main themes are improved control over the design process, better handling of input parameters, and more robust error checking.

### Main Themes and Innovations:

1.  **Enhanced Design Control and Customization:** The most significant innovation is the introduction of parameters for `starting_sequence` and `fixed_positions` in the `binder_hallucination` function. This allows users to provide an initial sequence and specify residues that should not change during the design process, offering much finer control over the output.
2.  **Improved Robustness and Flexibility:** The addition of `num_iters` and `threshold` parameters for the design stages provides more flexibility in balancing computational cost and design quality. The `clashes_flag` also allows for bypassing clash checks, which can be useful in certain experimental scenarios.
3.  **Bug Fixes and Refinements:** Several minor adjustments and a bug fix related to the seed sequence contribute to the overall stability and correctness of the design pipeline. The adjustment of the initial pLDDT requirement also indicates a tuning of the design parameters for potentially better initial results or broader applicability.

### Significant New Features or Improvements:

*   **`starting_sequence` and `fixed_positions` parameters:** Users can now guide the design process with a predefined starting sequence and specify positions that remain constant. This is a powerful feature for constrained design problems or for building upon known sequences.
*   **`num_iters` and `threshold` parameters:** These new parameters in `binder_hallucination` allow dynamic control over the number of iterations for the initial design stage and the pLDDT confidence threshold for continuing through the multi-stage design process.
*   **`clashes_flag`:** A new boolean flag to optionally ignore severe clash detection, which can be useful for specific research or debugging purposes.
*   **Refined pLDDT Thresholds:** The required initial pLDDT for continuing the design process has been lowered from 0.65 to 0.45, potentially allowing more designs to proceed through the pipeline, which might be beneficial for exploring a wider design space.
*   **Bug Fix for Seed Sequence:** A specific bug related to the seed sequence was addressed, improving the reliability of stochastic elements in the design.
*   **MPNN Sampling Batch Size:** The MPNN sequence sampling now correctly uses the `num_seqs` parameter for batching, which might improve performance or consistency.

### Notable Code Refactoring or Architectural Changes:

*   The `binder_hallucination` function's signature has been significantly expanded to accommodate the new input parameters.
*   New helper functions (`generate_wt_aatype`) or modifications to how `_wt_aatype`, `_cdr_positions`, `_core_positions`, and `_coupling_positions` are set on the `af_model` indicate an intention to support more complex sequence constraints and structural considerations.
*   The `predict_binder_complex` function was renamed to `masked_binder_predict`, suggesting a clearer semantic distinction for its purpose.

### Potential Impact or Value of the Changes:

These changes significantly increase the control and flexibility offered to users of the protein binder design tool. The ability to specify `starting_sequence` and `fixed_positions` is particularly valuable for:
*   **Directed Evolution:** Guiding designs towards specific sequence features.
*   **Optimization:** Refining existing binders by fixing known beneficial residues.
*   **Constraint Satisfaction:** Ensuring certain motifs or structural elements are maintained.
*   **Debugging and Analysis:** Isolating the effect of specific sequence changes.

The refined pLDDT thresholds and iteration controls also make the tool more adaptable to different design challenges and computational budgets. Overall, these changes make the design pipeline more versatile and robust for advanced protein design applications.

---

**Tags:**
*   feature
*   functionality
*   bugfix
*   improvement
*   refactor

**Commits:**

- [c1ae4863](/commit/c1ae486390f4da6d215e1ad0d7cc9d0a3b435dfb) - <span style="color:green">+6</span>/<span style="color:red">-2</span> (1 files): Update colabdesign_utils.py [skadaba1 <146038463+skadaba1@users.noreply.github.com>]

- [a5d28431](/commit/a5d284313ba7f979a190c6159bf0139a7fcdd95a) - <span style="color:green">+2</span>/<span style="color:red">-2</span> (1 files): Update colabdesign_utils.py [skadaba1 <146038463+skadaba1@users.noreply.github.com>]

- [a5119196](/commit/a5119196c8e8c2e07c0cad3b83ecec693dce1fce) - <span style="color:green">+7</span>/<span style="color:red">-7</span> (1 files): Update colabdesign_utils.py [skadaba1 <146038463+skadaba1@users.noreply.github.com>]

- [6750da54](/commit/6750da5482ed6bc468dab1faa65fdbc2c5e3249b) - <span style="color:green">+1</span>/<span style="color:red">-1</span> (1 files): Update colabdesign_utils.py [skadaba1 <146038463+skadaba1@users.noreply.github.com>]

- [957426e0](/commit/957426e0b4e4d2866de909aec2d968b25a7bce85) - <span style="color:green">+1</span>/<span style="color:red">-1</span> (1 files): Update colabdesign_utils.py [skadaba1 <146038463+skadaba1@users.noreply.github.com>]

- [ce2e36db](/commit/ce2e36dba28acf93425bcc830b29b1367f98240b) - <span style="color:green">+20</span>/<span style="color:red">-2</span> (1 files): Update colabdesign_utils.py [skadaba1 <146038463+skadaba1@users.noreply.github.com>]


---

### [A-Yarrow/BindCraft-Cloud](https://github.com/A-Yarrow/BindCraft-Cloud)

**Stats:**
- Commits ahead: 5
- Commits behind: 7
- Stars: 0

- Pull Requests:


- Last updated: 2025-06-24T17:06:51+00:00

**Summary of Changes:**
The changes in this fork primarily focus on enhancing the deployment and usability of Bindcraft, especially within a cloud environment like RunPod, and improving its installation process.

**Main Themes:**

*   **Cloud Deployment & Containerization:** Significant effort has been put into making Bindcraft runnable and manageable on cloud platforms, specifically RunPod, by leveraging Docker.
*   **Streamlined Installation:** The installation process for Bindcraft and its dependencies (like AlphaFold2 weights and PyRosetta) has been refined, moving away from `conda` for PyRosetta and integrating direct downloads.
*   **Jupyter Notebook Integration:** Jupyter notebooks are introduced to guide users through the installation, setup, and execution of Bindcraft, making it more accessible.

**Significant New Features or Improvements:**

*   **RunPod Integration (New `bindcraft-runpod-start.ipynb` and `start.sh`):**
    *   A dedicated Jupyter notebook (`bindcraft-runpod-start.ipynb`) is introduced to automate the setup steps for Bindcraft within a RunPod environment. This includes downloading AlphaFold2 weights and pulling the Bindcraft Docker image.
    *   The `start.sh` script is updated to facilitate the launch of this Jupyter notebook, streamlining the startup process on RunPod.
*   **Docker Integration and Checking:** The `bindcraft.ipynb` notebook now includes logic to check for Docker installation and attempts to pull the `yarrowdocker/bindcraft:latest` image, promoting a containerized workflow.
*   **Simplified PyRosetta Installation:** The `install_bindcraft.sh` script now uses `wget` to download PyRosetta directly instead of relying on `conda`, which can often be problematic for PyRosetta installations.
*   **Automated AlphaFold2 Weight Download:** The new RunPod notebook includes a bash cell to automatically download and extract AlphaFold2 model weights, a critical dependency for many protein-related tasks.

**Notable Code Refactoring or Architectural Changes:**

*   **Shift to Docker-centric Execution:** The introduction of Docker checks and image pulling in the notebooks suggests a strategic move towards a more robust, reproducible, and self-contained execution environment for Bindcraft.
*   **Jupyter as an Orchestration Layer:** The Jupyter notebooks are no longer just for interactive analysis but are now used as an orchestration layer to perform installation, dependency management, and even initiate the main Bindcraft process.
*   **Shell Scripting for Setup:** Increased use of `%%bash` cells within Jupyter notebooks and dedicated `start.sh` scripts for environment setup.

**Potential Impact or Value:**

*   **Increased Accessibility:** Lowering the barrier to entry for users, especially those less familiar with complex bioinformatics software installations, by providing guided Jupyter notebooks.
*   **Improved Reproducibility:** Leveraging Docker helps ensure that Bindcraft runs consistently across different environments, reducing "it works on my machine" issues.
*   **Easier Cloud Deployment:** Specifically tailored for RunPod, these changes make it significantly easier to spin up and use Bindcraft in a cloud GPU environment, which is crucial for computationally intensive tasks.
*   **Reduced Installation Headaches:** The move away from `conda` for PyRosetta addresses a common pain point for users.

**Tags:**
*   installation
*   feature
*   functionality
*   improvement
*   documentation
*   refactor

**Commits:**

- [f9ddf42a](/commit/f9ddf42a19f31fb92046ab6f4b143fb4f0345d88) - <span style="color:green">+117</span>/<span style="color:red">-0</span> (2 files): Updated bindcraft jupyter notebook and start.sh for runpod [A-Yarrow <yarrowmadrona@gmail.com>]

- [411f3ea9](/commit/411f3ea9bf54dfac7e390a99e65c3405c9db0b3b) - <span style="color:green">+155</span>/<span style="color:red">-29</span> (1 files): Added Docker check [A-Yarrow <yarrowmadrona@gmail.com>]

- [13863dc1](/commit/13863dc19e89ce08386fbc9421f4cbfd18c3fc11) - <span style="color:green">+12</span>/<span style="color:red">-39</span> (1 files): Finsishing up bindcraft install on jupyter lab [A-Yarrow <yarrowmadrona@gmail.com>]

- [10a263bf](/commit/10a263bf2d98a1f093614ddb6cc7d816f40cf8f6) - <span style="color:green">+200</span>/<span style="color:red">-0</span> (1 files): Added Bindcraft jupyter notebook [A-Yarrow <yarrowmadrona@gmail.com>]

- [854e13b7](/commit/854e13b75e4c93e7adb0e077b79a4eee293ea142) - <span style="color:green">+15</span>/<span style="color:red">-4</span> (1 files): Removed pyrosetta via conda and replaced with wget [A-Yarrow <yarrowmadrona@gmail.com>]


---

### [lullabee/BindCraft](https://github.com/lullabee/BindCraft)

**Stats:**
- Commits ahead: 5
- Commits behind: 8
- Stars: 0

- Pull Requests:


- Last updated: 2025-06-01T05:55:22+00:00

**Summary of Changes:**
This fork introduces several significant enhancements to the BindCraft project, primarily focusing on improved usability, new design capabilities, and better integration with cloud storage for result management.

**Main Themes:**

*   **Expanded Design Flexibility:** Introduction of "lenient filters" and a "medium" design target provides more options for users to control the stringency of their protein design parameters.
*   **Streamlined Execution:** The `start.sh` script simplifies the process of running BindCraft, making it more accessible.
*   **Cloud Integration for Results:** New scripts and modifications enable synchronization of results with Google Cloud Storage (GCS) and automated summary generation, improving data management and accessibility.

**Significant New Features or Improvements:**

*   **Lenient Filters:** Two new filter sets (`lenient_filters.json` and `lenient_plddt_filters.json`) allow for less strict filtering of design results, potentially yielding more candidates, especially for challenging design problems.
*   **Medium Design Target:** A new `cas_medium.json` target expands the scope of possible design sizes or complexities beyond the existing "small" targets.
*   **Simplified Startup:** The `start.sh` script encapsulates the environment setup and execution command, making it a one-command launch for users.
*   **Google Cloud Storage (GCS) Integration:** The `sync_results.sh` script, now optimized for cron jobs, facilitates automated uploading of results to GCS. This is complemented by `generate_summary.py` for creating summary reports of these cloud-stored results.
*   **Enhanced `.gitignore`:** A more comprehensive `.gitignore` file helps in maintaining a cleaner repository by excluding various build artifacts, virtual environment directories, IDE files, and BindCraft-specific output files.

**Notable Code Refactoring or Architectural Changes:**

*   Modifications to `bindcraft.py` to support the new filters and potentially the GCS synchronization aspects (though the direct GCS interaction seems to be primarily handled by shell scripts).
*   Addition of new configuration files (`.json`) for filters and design targets, promoting modularity in parameter definition.
*   Introduction of shell scripts (`start.sh`, `sync_results.sh`) and a Python script (`generate_summary.py`) external to the core `bindcraft.py`, indicating a move towards a more orchestrated workflow rather than a monolithic application.

**Potential Impact or Value of the Changes:**

These changes collectively make BindCraft more robust, user-friendly, and scalable, particularly for ongoing research or large-scale design campaigns. The lenient filters and new design target increase the versatility of the design capabilities. The `start.sh` script significantly lowers the barrier to entry for new users. Crucially, the GCS integration and summary generation automate data management and analysis, which is invaluable for long-running experiments or collaborative projects, ensuring results are backed up and easily accessible for review.

---
**Tags:**
*   feature
*   functionality
*   installation
*   improvement
*   documentation
*   ci (due to cron job integration)
*   refactor (due to external scripts and config files)

**Commits:**

- [4b081fa6](/commit/4b081fa6e20c85651f38d891351cf1fd690cbff3) - <span style="color:green">+884</span>/<span style="color:red">-56</span> (10 files): Introduced lenient filters and a new settings target for medium designs. Added start.sh script for easier execution. [Claire <clairedelaunay@gmail.com>]

- [0a0f098e](/commit/0a0f098e146732b8db49586cae985f52e434be24) - <span style="color:green">+80</span>/<span style="color:red">-6</span> (2 files): Update sync script to run in cron job [Claire Delaunay <clairedelaunay@gmail.com>]

- [5d6e4e6c](/commit/5d6e4e6ca7129a85e75c224780a71c8d9e78de0c) - <span style="color:green">+11</span>/<span style="color:red">-7</span> (1 files): Merge branch 'main' of https://github.com/lullabee/BindCraft [Claire Delaunay <clairedelaunay@gmail.com>]

- [3708e4fb](/commit/3708e4fbc168aee7d66724830145c8f700adbf52) - <span style="color:green">+2</span>/<span style="color:red">-1</span> (1 files): Add GCS integration and summary generation [Claire Delaunay <clairedelaunay@gmail.com>]

- [93290623](/commit/932906230f9ea1667c17c11d36b005b64ff5d8f8) - <span style="color:green">+217</span>/<span style="color:red">-0</span> (4 files): Scripts for gcd [Claire Delaunay <clairedelaunay@gmail.com>]


---

### [lindseyguan/BindCraft](https://github.com/lindseyguan/BindCraft)

**Stats:**
- Commits ahead: 4
- Commits behind: 13
- Stars: 0

- Pull Requests:


- Last updated: 2025-06-26T16:33:07+00:00

**Summary of Changes:**
The changes in this fork introduce significant improvements to the `bindcraft` protein design pipeline, primarily focusing on advanced optimization strategies and better handling of target and negative targets.

**Main Themes:**
*   **Joint Target Optimization:** The core innovation is the ability to optimize protein designs against multiple targets simultaneously, including "negative targets" to guide designs away from undesired binding interactions.
*   **Enhanced Design Control:** New parameters allow for more precise control over the design process, such as specifying an input binder for redesign and incorporating hotspot residues for the target.
*   **Improved Robustness and Logging:** The update includes better tracking of design metrics, improved clash detection, and more comprehensive logging for debugging and analysis.

**Significant New Features / Improvements:**
*   **Negative Target Optimization:** The introduction of `negative_targets` allows the model to learn to *not* bind to certain structures, which is crucial for specificity in drug discovery or protein engineering.
*   **Alternating Optimization:** The commit "alternating optimization, loss tracking, removing helix and rg from negative loss" suggests a more sophisticated optimization schedule, potentially leading to more stable and effective designs.
*   **Binder Redesign Capability:** The `redesign` flag and `binder_chain` parameter enable the pipeline to take an existing binder as input and optimize it, rather than starting from scratch.
*   **Target Hotspot Residues:** The `target_hotspot_residues` parameter in the `target` object allows users to specify critical residues on the target for the binder to interact with, guiding the design process more effectively.
*   **Improved Clash Detection Logging:** The output now explicitly prints the number of clashes after relaxation (`Num clashes - relaxed:`), which is valuable for assessing design quality.
*   **Settings File Copying:** Settings files are now copied to the output directory, ensuring reproducibility and easier tracking of parameters used for each design run.

**Notable Code Refactoring / Architectural Changes:**
*   **Introduction of `target` Object:** The creation of a `target` class (though its definition isn't in the diff, its usage is clear) centralizes target information, making the `binder_hallucination` function cleaner and more modular. This is a significant architectural improvement.
*   **Refined `binder_hallucination` Signature:** The `binder_hallucination` function now accepts `main_target` and `negative_targets` objects, streamlining the input parameters and reflecting the new optimization capabilities.
*   **Dynamic Binder Length and Redesign Logic:** The logic for determining binder length and whether to perform a redesign has been moved and enhanced to support the new `redesign` feature.

**Potential Impact or Value:**
These changes significantly enhance the `bindcraft` pipeline's utility for advanced protein design. The ability to perform joint optimization against multiple targets (including negative ones) is a powerful feature for designing highly specific binders, which is critical in fields like therapeutics and diagnostics. The improved control over design parameters and better logging also make the pipeline more robust and user-friendly for complex design challenges.

---

**Tags:**
*   feature
*   functionality
*   improvement
*   refactor

**Commits:**

- [34c744c7](/commit/34c744c74776e1d2a8495c84d9f0181937671203) - <span style="color:green">+133</span>/<span style="color:red">-74</span> (8 files): working on binder template input [Lindsey Guan <lindseyguan7@gmail.com>]

- [bb3911bf](/commit/bb3911bf92fc8d82983bf537b9160ab5d20b5950) - <span style="color:green">+99</span>/<span style="color:red">-22</span> (2 files): alternating optimization, loss tracking, removing helix and rg from negative loss [Lindsey Guan <lindseyguan7@gmail.com>]

- [20bf9102](/commit/20bf9102e0d38257c488cd76fbb470ed995e1a45) - <span style="color:green">+2443</span>/<span style="color:red">-40</span> (6 files): debugging why loss negation doesn't kick in immediately after called [Lindsey Guan <lindseyguan7@gmail.com>]

- [510da9ad](/commit/510da9ade4f8257e4e40bd32f359bd685423b9ca) - <span style="color:green">+57</span>/<span style="color:red">-12</span> (3 files): First attempt at joint target optimization [Lindsey Guan <lindseyguan7@gmail.com>]


---

### [y1zhou/NanobindCraft](https://github.com/y1zhou/NanobindCraft)

**Stats:**
- Commits ahead: 4
- Commits behind: 35
- Stars: 0

- Pull Requests:

  - [PR #1](https://github.com/martinpacesa/BindCraft/pull/93)


- Last updated: 2024-11-13T08:03:32+00:00

**Summary of Changes:**
The fork introduces significant refactoring and improvements to the `bindcraft.py` script, which appears to be the main entry point for the BindCraft protein design pipeline. The changes aim to improve code readability, maintainability, and potentially the robustness of the design process.

**Main Themes and Innovations:**

1.  **Code Restructuring and Modularity:** The monolithic `bindcraft.py` script has been broken down into more manageable, single-responsibility functions (`parse_input_paths`, `init_design_trajectory`, `mpnn_optimize_trajectory`). This significantly enhances code organization and makes it easier to understand individual steps of the protein design pipeline.
2.  **Explicit Imports:** Instead of a blanket `from functions import *`, the code now uses explicit imports, clearly showing which functions are used from each module. This improves code clarity and helps prevent naming conflicts.
3.  **Data Class for Trajectory Data:** The introduction of `TrajectoryData` (likely a `dataclass` from the `functions/generic_utils.py` module, though its definition isn't in this diff) to pass parameters between design stages is a key architectural improvement. This makes the data flow more structured and less error-prone compared to passing numerous individual arguments.
4.  **Improved MPNN Optimization Logic:** The `mpnn_optimize_trajectory` function encapsulates the complex multi-stage process of MPNN-based sequence optimization, including sequence generation, filtering, AF2 prediction, statistical analysis, and filter application. This centralizes the logic and makes it easier to reason about the MPNN design phase.
5.  **Enhanced Logging and Error Handling:** While not explicitly adding new error handling mechanisms, the refactoring allows for clearer logging and better identification of where issues might occur. The `init_design_trajectory` now returns `None` if a trajectory already exists or is terminated, allowing the main loop to skip it.
6.  **Minor Improvements and Bug Fixes:**
    *   Downgrading `flax` to ensure compatibility with `jax` and `pyrosetta` addresses a potential build issue.
    *   Suppression of various warnings (FutureWarning, DeprecationWarning, BiopythonWarning) cleans up the console output during execution.
    *   The random seed generation now uses `numpy.random.default_rng()` which is the recommended modern approach.
    *   The `mpnn_sequence` filtering now explicitly checks for sequence duplicates and restricted amino acids early on, potentially saving computational resources.

**Potential Impact and Value:**

*   **Maintainability:** The most significant impact is on the maintainability of the codebase. The modular design makes it much easier for developers to understand, debug, and extend specific parts of the pipeline without affecting others.
*   **Readability:** The code is now much more readable due to better organization, explicit imports, and well-defined functions.
*   **Robustness:** By encapsulating complex logic into functions and using structured data transfer (e.g., `TrajectoryData`), the pipeline becomes less prone to subtle bugs caused by incorrect parameter passing or implicit dependencies.
*   **Future Development:** The refactored structure provides a solid foundation for adding new features, algorithms, or analysis steps more easily in the future.

**Tags:**

*   refactor
*   functionality
*   improvement
*   documentation
*   build

**Commits:**

- [71736408](/commit/71736408e7981e37ce380c125cb470d09ed11ce0) - <span style="color:green">+71</span>/<span style="color:red">-34</span> (1 files): docs: add docstrings for the main loop functions [zhouyi <zhouyi@biomap.com>]

- [cef33888](/commit/cef3388811da4a0906473843055695d3432a6565) - <span style="color:green">+5186</span>/<span style="color:red">-36166</span> (25 files): Merge remote-tracking branch 'upstream/v1.2.0' [Yi Zhou <zhouyi@biomap.com>]

- [f731bb68](/commit/f731bb6857b7c3312a46691e04d8748fecdc43ec) - <span style="color:green">+937</span>/<span style="color:red">-434</span> (4 files): refactor(main): make the main entry script clear to read [zhouyi <zhouyi@biomap.com>]

- [70adfcdb](/commit/70adfcdbdf501d856c2e4a61c89e8234d31be2ab) - <span style="color:green">+166</span>/<span style="color:red">-2</span> (2 files): build: downgrade flax to make jax and pyrosetta work together [y1zhou <zhouyi@biomap.com>]


---

### [maxall41/BindCraft](https://github.com/maxall41/BindCraft)

**Stats:**
- Commits ahead: 4
- Commits behind: 37
- Stars: 0

- Pull Requests:


- Last updated: 2024-11-02T07:09:55+00:00

**Summary of Changes:**
The user has provided a series of commits and a combined diff for the `install_bindcraft.sh` script.

**Summary of Changes:**

The changes primarily focus on streamlining and simplifying the installation process for BindCraft, particularly concerning its Conda environment and dependencies. The key theme is reducing the complexity and verbosity of the installation script by removing extensive error checking, explicit Conda environment activation/deactivation, and detailed package validation steps.

**Innovation/Improvements:**

1.  **Simplified Conda Management:** The script no longer explicitly creates, activates, or deactivates a dedicated `BindCraft` Conda environment. Instead, it relies on the current Conda environment (or a system-wide installation if `conda` is not sourced) to install packages. This could simplify the script's execution flow but might make the installation less isolated if not run within a pre-configured environment.
2.  **Reduced Verbosity and Error Handling:** Much of the detailed error checking for Conda environment existence, package installation success, and file integrity (e.g., AlphaFold2 weights) has been removed. This makes the script shorter and potentially faster to execute, but it also reduces its robustness in handling unexpected installation failures.
3.  **Hardcoded Installation Directory:** The `install_dir` is now hardcoded to `/root/bindcraft/` instead of `$(pwd)`. This implies a specific deployment scenario, possibly within a containerized environment like Docker, where `/root/bindcraft/` is the expected root for the application.
4.  **Minor Package List Adjustment:** The `libgfortran5` and `flax"<0.10.0"` packages were removed from the installation list for both CUDA and non-CUDA paths, and `anaconda` channel was added.

**Potential Impact/Value:**

*   **Positive:**
    *   **Simpler Script:** The script is more concise and easier to read due to the removal of many checks and explicit Conda commands.
    *   **Potentially Faster Execution:** Less overhead from environment checks and activations could lead to quicker installation times.
    *   **Containerization Focus:** The hardcoded install path suggests an optimization for containerized deployments, where the root directory is predictable.
*   **Negative:**
    *   **Reduced Robustness:** The removal of extensive error checking means the script is less resilient to failures. If an installation step fails, the script might continue without proper indication, leading to a broken installation that is harder to debug.
    *   **Less Isolation:** Without explicit environment creation and activation, the installation might interfere with existing Conda environments or system-wide Python installations if not run in a controlled environment.
    *   **Less User-Friendly:** The removal of detailed status messages and error prompts makes it harder for a user to understand what's happening or diagnose issues if something goes wrong.

**Tags:**

*   installation
*   refactor
*   improvement

**Commits:**

- [ad149cc4](/commit/ad149cc4899e5dadec7668179ace7314b437b4d6) - <span style="color:green">+1</span>/<span style="color:red">-1</span> (1 files): Update install_bindcraft.sh [Max Campbell <41460735+maxall41@users.noreply.github.com>]

- [1a26bbb5](/commit/1a26bbb5a0d627915d069a7247eef1409ce5eadc) - <span style="color:green">+2</span>/<span style="color:red">-4</span> (1 files): Update install_bindcraft.sh [Max Campbell <41460735+maxall41@users.noreply.github.com>]

- [c0c03c08](/commit/c0c03c08313d9c2196fe903b454fbe898c839e9f) - <span style="color:green">+1</span>/<span style="color:red">-5</span> (1 files): Update install_bindcraft.sh [Max Campbell <41460735+maxall41@users.noreply.github.com>]

- [82689152](/commit/82689152e3f3fc750bed973e4a7206c2489bebda) - <span style="color:green">+0</span>/<span style="color:red">-3</span> (1 files): Update install_bindcraft.sh [Max Campbell <41460735+maxall41@users.noreply.github.com>]


---

### [tetmin/BindCraft](https://github.com/tetmin/BindCraft)

**Stats:**
- Commits ahead: 4
- Commits behind: 47
- Stars: 0

- Pull Requests:


- Last updated: 2024-10-10T14:01:42+00:00

**Summary of Changes:**
This fork primarily focuses on repository hygiene and maintainability, particularly for machine learning (LLM) parsing tools like `uithub` and for version control.

**Main themes and purposes:**

*   **Repository Cleanliness:** The most significant changes involve removing large, unnecessary files (specifically Jupyter notebook outputs) from the repository. This reduces repository size and improves cloning/fetching performance.
*   **LLM Parsing Configuration:** Introduction and refinement of a `.genignore` file, which is likely used by an LLM parsing tool (e.g., `uithub`) to specify files or directories to ignore during its analysis. This helps focus the LLM on relevant source code.

**Significant new features or improvements:**

*   **`.genignore` file:** A new `.genignore` file is added to explicitly exclude certain paths (e.g., `example/*`, specific JSON filter files) from being processed by an LLM parsing tool. This is a new configuration aspect.
*   **Cleaned Jupyter Notebooks:** Jupyter notebook outputs are cleared, which is a significant improvement for version control and collaboration as it prevents large, frequently changing binary data from cluttering diffs and history.

**Notable code refactoring or architectural changes:**

*   No architectural changes or significant code refactoring beyond the `.genignore` configuration. The changes are primarily related to file management and repository configuration.

**Potential impact or value of the changes:**

*   **Improved Developer Experience:** Smaller repository size and cleaner diffs for Jupyter notebooks make it easier for developers to clone, pull, and review changes.
*   **Enhanced LLM Analysis:** The `.genignore` file helps LLM parsing tools like `uithub` focus on relevant code, potentially leading to more accurate and efficient analysis.
*   **Reduced Storage Costs:** For large repositories, removing binary outputs can significantly reduce storage requirements.

---

**Tags:**

*   `refactor`
*   `improvement`
*   `documentation` (indirectly, as it cleans up content that might be parsed by LLMs)

**Commits:**

- [5fbd0f52](/commit/5fbd0f524bc89293421b097fa056e251f4e43ac7) - <span style="color:green">+3</span>/<span style="color:red">-3</span> (1 files): corrects .genignore [Tom Etminan <tetmin@gmail.com>]

- [85e73628](/commit/85e73628f1afd44777a33bfdc963a9951387abb7) - <span style="color:green">+3</span>/<span style="color:red">-0</span> (1 files): adds .genignore for uithub LLM parsing [Tom Etminan <tetmin@gmail.com>]

- [e5bddfa9](/commit/e5bddfa91f2b60caedb3bf792f4e0552bcfcad6c) - <span style="color:green">+4</span>/<span style="color:red">-34494</span> (1 files): clears more ipynb outputs [Tom Etminan <tetmin@gmail.com>]

- [50ac42df](/commit/50ac42df79121659ea7ae69bb576f2d9a9df691b) - <span style="color:green">+187</span>/<span style="color:red">-1464</span> (1 files): removes .ipynb cell outputs [Tom Etminan <tetmin@gmail.com>]


---

### [bmwoolf/BindCraft](https://github.com/bmwoolf/BindCraft)

**Stats:**
- Commits ahead: 3
- Commits behind: 7
- Stars: 0

- Pull Requests:


- Last updated: 2025-06-11T03:27:22+00:00

**Summary of Changes:**
This fork primarily focuses on minor textual corrections within the `bindcraft.py` file.

**Summary of Changes:**

The main purpose of these changes is to correct spelling errors. There are no new features, significant refactoring, or architectural changes introduced. The impact is minimal, improving the readability of comments or strings within the code.

**Tags:**
- "bugfix"

**Commits:**

- [96c6d987](/commit/96c6d9873b7bc4f78f8e811dbe6d0d45b1bb95c8) - <span style="color:green">+0</span>/<span style="color:red">-0</span> (0 files): Merge branch 'main' of https://github.com/bmwoolf/BindCraft [bmwoolf <bradleymwoolf@gmail.com>]

- [e633bbf6](/commit/e633bbf6efad7c7fc2667ed5a6afe8b08fd6bce3) - <span style="color:green">+2</span>/<span style="color:red">-2</span> (1 files): spelling [bmwoolf <bradleymwoolf@gmail.com>]

- [2996f90f](/commit/2996f90f510f21671fbbf05c585f6821f8904663) - <span style="color:green">+2</span>/<span style="color:red">-2</span> (1 files): spelling [bmwoolf <bradleymwoolf@gmail.com>]


---

### [benediktsinger/BindCraft-uv](https://github.com/benediktsinger/BindCraft-uv)

**Stats:**
- Commits ahead: 3
- Commits behind: 15
- Stars: 0

- Pull Requests:


- Last updated: 2025-04-02T17:23:02+00:00

**Summary of Changes:**
This fork introduces several changes primarily focused on improving the installation process, refining Slurm job submission, and addressing minor configuration bugs.

**Main Themes:**

*   **Installation Modernization:** Shifting from `conda` to `uv` for dependency management.
*   **Slurm Integration Refinement:** Enhancements to the Slurm submission script for better job management and environment activation.
*   **Bug Fixing:** Minor adjustments to configuration files to resolve issues.

**Significant New Features or Improvements:**

*   **`uv` for Installation:** A new `install_bindcraft_uv.sh` script is introduced, leveraging `uv` for faster and more reliable dependency resolution and installation within a virtual environment. This is a significant improvement over potentially slower and more complex `conda` setups.
*   **Improved Slurm Script (`bindcraft.slurm`):**
    *   The `qos=gpu` directive is removed, potentially simplifying job queueing on some Slurm systems.
    *   The script now explicitly activates a `bindcraft_venv` (presumably created by `uv`), providing clearer environment management.
    *   The method for determining `SCRIPT_DIR` is made more robust by using `scontrol show job $SLURM_JOB_ID` to get the actual script path, which can be more reliable than `dirname "$0"` in certain Slurm execution contexts.

**Notable Code Refactoring or Architectural Changes:**

*   **`pyproject.toml` Integration:** The `pyproject.toml` file is added, indicating a move towards a more standardized Python project structure and build system (likely leveraging `setuptools` or `hatch` as managed by `uv`). This file contains extensive dependency declarations, moving away from a separate `requirements.txt` or sole reliance on `conda` environments.
*   **Decoupling from `CONDA_BASE`:** The `bindcraft.slurm` script reduces its direct reliance on `CONDA_BASE` by activating a dedicated `bindcraft_venv`, making it more flexible for non-conda installations.

**Potential Impact or Value:**

*   **Faster and More Reliable Installation:** The adoption of `uv` should significantly speed up the installation process and reduce common dependency conflicts, improving the developer and user experience.
*   **Enhanced Slurm Usability:** The updated Slurm script provides more robust and clearer environment activation, making it easier to run `bindcraft` jobs on HPC clusters.
*   **Improved Project Maintainability:** The introduction of `pyproject.toml` aligns the project with modern Python packaging standards, potentially simplifying future dependency management and distribution.
*   **Reduced Configuration Headaches:** The bug fixes in JSON configuration files ensure the application runs correctly with intended settings.

**Tags:**
*   installation
*   functionality
*   bugfix
*   improvement
*   refactor
*   ci (indirectly, as `pyproject.toml` and `uv` setup can simplify CI/CD)

**Commits:**

- [4b7b6492](/commit/4b7b64920daa822f2c9bcd6691c2056866438a54) - <span style="color:green">+0</span>/<span style="color:red">-1</span> (1 files): Update bindcraft.slurm [Benedikt Singer <82055049+benediktsinger@users.noreply.github.com>]

- [866b14bb](/commit/866b14bba4e020ceea00542546125f071473ff65) - <span style="color:green">+4</span>/<span style="color:red">-4</span> (2 files): More bugfixes [Benedikt Singer <singer@i21.izar.cluster>]

- [999f4973](/commit/999f4973b95e0db0fbaaa6c83d769ee27a3aa4af) - <span style="color:green">+364</span>/<span style="color:red">-2</span> (3 files): Bugfixes and change installation to uv [Benedikt Singer <singer@izar1.izar.cluster>]


---

### [WBennett003/BindCraft_SharpLab](https://github.com/WBennett003/BindCraft_SharpLab)

**Stats:**
- Commits ahead: 3
- Commits behind: 19
- Stars: 0

- Pull Requests:


- Last updated: 2025-03-08T21:30:48+00:00

**Summary of Changes:**
This fork introduces a significant new feature: a "custom pipeline" functionality for the BindCraft protein design framework. This allows users to define and execute multi-stage design workflows, integrating various computational tools.

**Main Themes and Innovations:**

*   **Customizable Design Pipelines:** The core innovation is the `custom_pipeline` method within the `binder_designer` class. This method allows users to define a sequence of design "jobs" (e.g., AF2Design, SolubleMPNN, Complex_prediction, Fampnn, DiffDock-ppi, Chai), each with specified inputs and outputs. This moves beyond a fixed workflow, offering greater flexibility and control over the protein design process.
*   **Integration of External Tools:** The fork explicitly integrates and manages external computational tools like Fampnn, DiffDock-PP, and PepFlow. This is evident from the new `FullAtomMPNN_handler`, `DiffDockPP_handler`, and `PepFlow_handler` classes, as well as the inclusion of their respective tool directories (`tools/fampnn`, `tools/DiffDock-PP`, `tools/pepflow`).
*   **Improved Logging and Tracking (WandB):** The introduction of `wandb_handler` suggests an intention to integrate Weights & Biases for better experiment tracking, logging of design metrics, and visualization of results.
*   **Enhanced MSA and Templating:** The `run_msa_templating` function and related changes indicate a more sophisticated approach to handling multiple sequence alignments and structural templates, including options for different MSA methods (e.g., MMseqs2) and template propagation.
*   **Modular Design:** The refactoring into a `binder_designer` class with distinct methods for each step (e.g., `generate_trajectory`, `score_trajectory`, `soluble_mpnn_optimisation`, `predict_complex`, `filter_designs`) promotes modularity and reusability.

**Significant New Features / Improvements:**

*   **`bindcraft_custom.py`:** This new central file orchestrates the custom design pipeline.
*   **`custom_pipeline` method:** Enables sequential execution of user-defined design steps.
*   **Tool Handlers:** `DiffDockPP_handler`, `FullAtomMPNN_handler`, `PepFlow_handler` classes facilitate the use of these external tools.
*   **WandB Integration:** `wandb_handler` for experiment logging.
*   **Advanced Templating Options:** Support for various MSA and templating modes, including handling of homooligomers and cyclic sequences.
*   **JAX Memory Management:** `clear_mem()` function to manage JAX buffers, potentially improving memory efficiency.

**Notable Code Refactoring / Architectural Changes:**

*   **Object-Oriented Structure:** The transition to a `binder_designer` class encapsulates the entire design logic, making it more robust and extensible.
*   **Separation of Concerns:** Individual steps like trajectory generation, MPNN optimization, complex prediction, and filtering are now distinct methods, improving code organization.
*   **Configuration Management:** Use of `omegaconf.DictConfig` suggests a more structured way to manage configurations for different design stages.

**Potential Impact / Value:**

This fork significantly enhances the flexibility and power of BindCraft. By allowing users to define custom pipelines and integrate a broader range of external tools, it enables more complex and tailored protein design experiments. This could lead to:

*   **Accelerated Research:** Researchers can quickly prototype and test new design strategies by combining different computational methods.
*   **Broader Applicability:** The ability to incorporate specialized tools (like DiffDock-PP for docking or Fampnn for full-atom MPNN) expands BindCraft's utility to a wider array of protein design problems.
*   **Reproducibility:** With WandB integration, tracking and reproducing complex multi-stage designs becomes easier.
*   **Community Contribution:** The modular structure makes it easier for others to contribute new design steps or integrate additional tools.

**Tags:**

*   feature
*   functionality
*   refactor
*   improvement
*   installation (due to new tool dependencies and environment setup)

**Commits:**

- [da3019b5](/commit/da3019b5b721ac11ae74ff9f57bb28173a282e40) - <span style="color:green">+10</span>/<span style="color:red">-2</span> (2 files): added some more custom pipeline stuff [Will Bennett <vi21227@it107030.users.bris.ac.uk>]

- [87bd9a95](/commit/87bd9a951c2a69173198ff9f8c4c4a56c07383e9) - <span style="color:green">+845</span>/<span style="color:red">-171</span> (7 files): added custom pipeline [Will Bennett <vi21227@it107030.users.bris.ac.uk>]

- [e362ecbc](/commit/e362ecbc75b3bcd8f299fefb7c1d307999137a21) - <span style="color:green">+605</span>/<span style="color:red">-1</span> (7 files): First-commit [will bennett <vi21227@bristol.ac.uk>]


---

### [eesb99/BindCraft](https://github.com/eesb99/BindCraft)

**Stats:**
- Commits ahead: 3
- Commits behind: 35
- Stars: 0

- Pull Requests:


- Last updated: 2024-11-06T14:13:40+00:00

**Summary of Changes:**
The user wants a summary of changes in the provided diff.

**Summary of Changes and Innovations in the Fork:**

This fork primarily focuses on **improving the robustness and usability of the BindCraft protein binder design pipeline within a Google Colab environment**. The core innovation lies in addressing potential instability issues related to file access and handling within the Colab/Google Drive setup, which can be crucial for long-running computational tasks like protein design.

**Main Themes:**

*   **Enhanced Stability and Error Handling:** The most significant change is the introduction of a robust file access mechanism to prevent failures due to transient file system issues, particularly when interacting with Google Drive.
*   **Improved User Experience in Colab:** The notebook is made more resilient to common Colab quirks, such as file synchronization delays.
*   **Minor Refinements to Workflow:** There are small adjustments to the setup and execution flow within the Jupyter notebook, making it potentially smoother for users.

**Significant New Features or Improvements:**

*   **`safe_file_access` Function:** A new utility function `safe_file_access` has been added. This function attempts to access a given file with retries and delays, effectively mitigating issues where files might not be immediately available after being written to Google Drive, or where PyRosetta might fail to open files due to such delays. This directly addresses a critical point of failure in a Colab-based workflow.
*   **Explicit Directory Creation:** The notebook now includes a dedicated cell to explicitly create the full hierarchical directory structure within Google Drive (`/content/drive/My Drive/BindCraft/PDL1/Trajectory`, `/MPNN`, `/Accepted`, etc.) before starting the design process. This pre-emptive directory creation ensures a more stable and predictable file organization.
*   **Removed Redundant `prediction_protocol` Option:** The "prediction_protocol" advanced setting, which previously had "Default" and "HardTarget" options, has been removed. This simplifies the advanced settings by removing what might have been a less critical or redundant parameter.
*   **Updated `trajectory.aux` Access:** The way trajectory metrics are accessed has been updated from `trajectory._tmp["best"]["aux"]["log"]` to `trajectory.aux["log"]`. This indicates a potential update in the underlying `ColabDesign` library's API or a correction in how auxiliary logs are retrieved.

**Notable Code Refactoring or Architectural Changes:**

*   **Inclusion of `safe_file_access` Logic:** The `pr_relax` call within the main design loop is now wrapped with the `safe_file_access` function. This is a crucial architectural change for stability, ensuring that PyRosetta only attempts to process PDB files after they are confirmed to be accessible.
*   **Streamlined Advanced Settings Logic:** The `advanced_settings_path` construction has been simplified by removing the `prediction_protocol_tag`, aligning with the removal of that option from the UI.
*   **Pre-execution Directory Setup:** Moving the directory creation to a separate, explicit cell at the beginning of the notebook's setup phase is a refactoring that improves clarity and reliability.

**Potential Impact or Value of the Changes:**

These changes significantly enhance the **reliability and user-friendliness** of the BindCraft pipeline when run in a Google Colab environment. By proactively handling common file system and synchronization issues, the fork is less prone to crashes and allows for more stable, long-running design campaigns. This directly translates to increased productivity for users who rely on Colab for their protein design work, as they will experience fewer interruptions and data corruption issues. The explicit directory creation also makes the setup more transparent and less error-prone for new users.

---

**Tags:**

*   `bugfix` (Addressing issues with file access and PyRosetta errors)
*   `improvement` (Enhanced stability, reliability, and user experience)
*   `refactor` (Changes to how settings are handled, and the introduction of a utility function)
*   `functionality` (Improved file handling logic)
*   `ui` (Minor changes to Colab UI inputs by removing an option)

**Commits:**

- [cf38b0fe](/commit/cf38b0fecc0733a3a855668efc7bb466218aaedf) - <span style="color:green">+209</span>/<span style="color:red">-54</span> (1 files): Created using Colab [eesb99 <61354428+eesb99@users.noreply.github.com>]

- [ba2026aa](/commit/ba2026aabe546043a7e8ef3f48d4d6f9e145e4ac) - <span style="color:green">+290</span>/<span style="color:red">-210</span> (1 files): Created using Colab [eesb99 <61354428+eesb99@users.noreply.github.com>]

- [5cdd7346](/commit/5cdd7346c8a3e8b9c3fe9117c95c27e1fb167842) - <span style="color:green">+610</span>/<span style="color:red">-29</span> (1 files): Created using Colab [eesb99 <61354428+eesb99@users.noreply.github.com>]


---

### [cytokineking/BindCraft-PR-optional](https://github.com/cytokineking/BindCraft-PR-optional)

**Stats:**
- Commits ahead: 2
- Commits behind: 10
- Stars: 0

- Pull Requests:


- Last updated: 2025-05-20T18:37:50+00:00

**Summary of Changes:**
This fork introduces **BindCraft**, a new tool, into the repository, with a focus on making its PyRosetta dependency optional.

### Main Themes and Innovations:

1.  **Introduction of BindCraft:** The primary change is the addition of `bindcraft.py` and associated utility functions, indicating the integration of a new computational design tool.
2.  **Optional PyRosetta Dependency:** A significant architectural decision has been made to make PyRosetta an optional dependency for BindCraft. This enhances the tool's accessibility and ease of use, as PyRosetta can be complex to install and license. This is evident from the `pyrosetta_utils.py` file and the commit message "Initial commit of PyRosetta-optional BindCraft".
3.  **Streamlined Installation:** The inclusion of `install_bindcraft.sh` suggests an effort to simplify the installation process for users, making the new tool easier to set up.
4.  **Configuration for Peptide Design:** The addition of `cyclize_peptide: false` to numerous advanced settings JSON files indicates a specific configuration adjustment for peptide design workflows, potentially to disable peptide cyclization by default in various multimer design scenarios.

### Significant New Features or Improvements:

*   **BindCraft Tool:** A new, presumably powerful tool for computational design (likely protein/peptide binding design) is introduced.
*   **Flexible Dependency Management:** The optional PyRosetta dependency is a major improvement for usability, allowing users to run BindCraft without a full PyRosetta installation if certain functionalities are not required.
*   **Automated Installation Script:** `install_bindcraft.sh` aims to provide an easier setup experience for BindCraft.

### Notable Code Refactoring or Architectural Changes:

*   **Modular Utilities:** The `functions` directory containing `biopython_utils.py`, `colabdesign_utils.py`, `generic_utils.py`, and `pyrosetta_utils.py` indicates a modular design for utility functions, promoting reusability and maintainability.
*   **Configuration Management:** The widespread modification of advanced settings JSON files (`settings_advanced/*.json`) suggests a structured approach to managing different design parameters and workflows.

### Potential Impact or Value:

This fork provides a valuable new computational design tool, BindCraft, to the user base. By making PyRosetta optional, it significantly lowers the barrier to entry for many potential users who might otherwise be deterred by PyRosetta's installation complexity or licensing. The streamlined installation script further enhances usability. The specific configuration changes for peptide cyclization suggest fine-tuned control over design parameters for various multi-stage, multimer design scenarios, which could be critical for successful computational design.

### Tags:

*   feature
*   functionality
*   refactor
*   improvement
*   installation

**Commits:**

- [680050f3](/commit/680050f30b29f1dcd8f30dbe8c931e04a264bb29) - <span style="color:green">+22</span>/<span style="color:red">-0</span> (21 files): Added "cyclize_peptide": false to all advanced settings [Aaron Ring <aaronring@gmail.com>]

- [107ec42d](/commit/107ec42dd3f7e02348c8bca2fbe880301784d9fa) - <span style="color:green">+987</span>/<span style="color:red">-242</span> (9 files): Initial commit of PyRosetta-optional BindCraft [Aaron Ring <aaronring@gmail.com>]


---

### [outpace-bio/BindCraft](https://github.com/outpace-bio/BindCraft)

**Stats:**
- Commits ahead: 2
- Commits behind: 19
- Stars: 0

- Pull Requests:


- Last updated: 2025-04-29T20:13:55+00:00

**Summary of Changes:**
This fork introduces significant updates primarily focused on enhancing the deployment and functionality of the `bindcraft` tool, likely related to protein binding or design, leveraging machine learning.

The main themes of these changes are:
1.  **Dockerization for Reproducibility and Ease of Use**: A new `Dockerfile` is introduced to containerize the application, ensuring a consistent environment for running `bindcraft` with all its dependencies, including CUDA, Conda, and specific Python libraries.
2.  **Integration of Machine Learning Dependencies**: The `Dockerfile` explicitly installs a comprehensive set of scientific computing and machine learning libraries (e.g., `jax`, `jaxlib`, `dm-haiku`, `optax`, `ColabDesign`, `AlphaFold2` weights), indicating that `bindcraft` now heavily relies on or integrates with advanced AI/ML models for its core functionality.
3.  **Refactored `bindcraft.py`**: The main `bindcraft.py` script has undergone substantial changes, likely to incorporate the new ML functionalities and potentially improve its overall architecture or user interface.

**Significant New Features or Improvements:**
*   **Docker Support**: Users can now easily build and run `bindcraft` within a Docker container, simplifying setup and dependency management, especially for GPU-accelerated tasks.
*   **Deep Learning Capabilities (via ColabDesign/AlphaFold2)**: The inclusion of `ColabDesign` and `AlphaFold2` weights strongly suggests that `bindcraft` now has capabilities for protein design, structure prediction, or related tasks that leverage state-of-the-art deep learning models in structural biology. This is a major functional enhancement.
*   **Comprehensive ML/Scientific Stack**: The Docker image provides a complete environment with `CUDA`, `cuDNN`, `JAX`, `PyTorch` (via `pyrosetta` and potentially others), `pandas`, `matplotlib`, `numpy`, `scipy`, `biopython`, `pdbfixer`, `seaborn`, `tqdm`, `jupyter`, `ffmpeg`, `fsspec`, `py3dmol`, `chex`, `dm-haiku`, `dm-tree`, `joblib`, `ml-collections`, `immutabledict`, `optax`, enabling complex computational biology workflows.

**Notable Code Refactoring or Architectural Changes:**
*   **Containerization**: This is a major architectural shift, moving towards a more robust and portable deployment model.
*   **Dependency Management via Conda and Pip in Docker**: The `Dockerfile` orchestrates the installation of all necessary libraries, using Conda for core scientific packages and pip for specific projects like `ColabDesign`.
*   **`bindcraft.py` Refactoring**: While the specific changes aren't detailed in the diff, the high number of insertions and deletions in `bindcraft.py` indicate a significant overhaul, likely to integrate the new ML functionalities and potentially improve modularity or command-line interface.

**Potential Impact or Value of the Changes:**
*   **Increased Accessibility**: Docker makes `bindcraft` much easier to install and run, especially for users without deep knowledge of dependency management or GPU setup.
*   **Enhanced Research Capabilities**: The integration of `ColabDesign` and `AlphaFold2` weights transforms `bindcraft` into a more powerful tool for advanced protein engineering, drug discovery, or structural biology research, enabling experiments that leverage cutting-edge AI.
*   **Reproducibility**: The Docker image ensures that results obtained with `bindcraft` are more easily reproducible across different environments.
*   **Performance**: Leveraging CUDA and JAX indicates a focus on high-performance computing, crucial for deep learning models.

**Tags:**
*   installation
*   feature
*   functionality
*   refactor
*   improvement

**Commits:**

- [51132635](/commit/51132635a269ae9164b044d4e50c6ee96bc33ef8) - <span style="color:green">+38</span>/<span style="color:red">-0</span> (1 files): Docker updates [Bobby Langan <rlangan@outpacebio.com>]

- [67b0013a](/commit/67b0013a575c5ea3ef6092818e7fdd12aafcd1b5) - <span style="color:green">+551</span>/<span style="color:red">-162</span> (1 files): Docker updates [Bobby Langan <rlangan@outpacebio.com>]


---

### [PartialBark7/BindCraft](https://github.com/PartialBark7/BindCraft)

**Stats:**
- Commits ahead: 2
- Commits behind: 15
- Stars: 0

- Pull Requests:


- Last updated: 2025-03-29T11:13:11+00:00

**Summary of Changes:**
The user has provided a single Jupyter Notebook file (`notebooks/BindCraft.ipynb`) with two commits. The diff shows a significant number of insertions and deletions, indicating substantial changes to the notebook's content.

### Summary of Changes:

This fork introduces significant enhancements and refactoring to the `BindCraft` protein binder design pipeline, primarily within a Google Colab environment. The changes focus on improving the user experience, enhancing the design process, and refining the output analysis.

**Main Themes:**

*   **Improved User Interface and Workflow:** The notebook has been restructured to be more user-friendly within Colab, with clear sections for installation, settings, and execution, utilizing Colab's form features.
*   **Enhanced Design Protocols and Customization:** New options for advanced design and filtering protocols have been added, allowing users more control over the binder design process.
*   **Richer Data Collection and Analysis:** The pipeline now collects more comprehensive metrics at various stages of design (trajectory, MPNN, final designs) and stores them in structured CSV files, facilitating better analysis and tracking of design performance.
*   **Robustness and Error Handling:** Minor improvements in checks and error handling are visible, particularly around file existence and data processing.

**Significant New Features or Improvements:**

*   **Colab Integration Enhancements:**
    *   Added a "view-in-github" badge for better discoverability.
    *   Implemented live updates for "Sampled Trajectories" and "Accepted Designs" using `ipywidgets.HTML` and `VBox`, providing immediate feedback during long-running processes.
*   **Advanced Settings for Design Protocols:**
    *   Introduced `design_protocol` (Default, Beta-sheet, Peptide) to tailor the design strategy.
    *   Added `prediction_protocol` (Default, HardTarget) for controlling AlphaFold2 prediction behavior.
    *   Introduced `interface_protocol` (AlphaFold2, MPNN) for optimizing the binder-target interface.
    *   Added `template_protocol` (Default, Masked) for controlling target flexibility.
    *   These selections dynamically generate the path to corresponding JSON configuration files.
*   **Flexible Filtering Options:**
    *   Added `filter_option` (Default, Peptide, Relaxed, Peptide_Relaxed, None) to apply different sets of criteria for accepted designs, improving control over design quality.
*   **Comprehensive Data Logging and Persistence:**
    *   Introduced `trajectory_csv`, `mpnn_csv`, `final_csv`, and `failure_csv` for detailed logging of design metrics, MPNN design statistics, final accepted designs, and filter failures, respectively. This is a major improvement for reproducibility and analysis.
    *   The `check_accepted_designs` and `check_n_trajectories` functions enable continuation of design campaigns and limit run-time.
*   **Detailed Metric Collection:**
    *   Expanded the metrics collected for each design trajectory, including `i_pLDDT`, `ss_pLDDT`, `Unrelaxed_Clashes`, `Relaxed_Clashes`, various interface scores (e.g., `Binder_Energy_Score`, `ShapeComplementarity`, `dG`, `dSASA`, `Interface_Hydrophobicity`), secondary structure percentages for both the binder and interface, and RMSD values (`Hotspot_RMSD`, `Target_RMSD`).
*   **Improved MPNN Integration and Filtering:**
    *   Enhanced the MPNN sequence generation and prediction loop, including handling of restricted amino acids and duplicate sequences.
    *   The `predict_binder_complex` and `predict_binder_alone` functions now return more detailed statistics.
*   **Post-Design Analysis and Visualization:**
    *   Added sections for "Consolidate & Rank Designs", "Top 20 Designs" (displaying a dataframe head), "Top Design Display" (using `py3Dmol`), and "Display animation" for the top-ranked design. These significantly improve the post-processing and visual inspection capabilities.

**Notable Code Refactoring or Architectural Changes:**

*   **Modularization of Settings:** The settings are now loaded from external JSON files (`settings_advanced/` and `settings_filters/`), making the notebook cleaner and easier to manage different configurations without direct code modification.
*   **Refined Data Structures:** The use of `trajectory_labels`, `design_labels`, and `final_labels` for CSV headers, along with `copy_dict` and structured dictionaries for `trajectory_metrics`, `mpnn_complex_statistics`, and `binder_statistics`, indicates a more organized approach to data handling.
*   **Clearer Workflow Logic:** The main design

**Commits:**

- [4641b01a](/commit/4641b01a78bfe4d8aace35c45b7df2da350d3611) - <span style="color:green">+212</span>/<span style="color:red">-67</span> (1 files): Created using Colab [PartialBark7 <alice.milne92@googlemail.com>]

- [3758ce13](/commit/3758ce13c01495b5d894a6fdc128990c4bdc1f60) - <span style="color:green">+1319</span>/<span style="color:red">-891</span> (1 files): Created using Colab [PartialBark7 <alice.milne92@googlemail.com>]


---

### [gattil/BindCraft](https://github.com/gattil/BindCraft)

**Stats:**
- Commits ahead: 2
- Commits behind: 15
- Stars: 0

- Pull Requests:


- Last updated: 2025-03-25T17:08:15+00:00

**Summary of Changes:**
This fork introduces significant changes primarily focused on improving the portability and ease of deployment of the `BindCraft` application through the adoption of Docker.

### Main Themes and Innovations:

1.  **Dockerization for Reproducibility and Portability:** The core innovation is the introduction of a `Dockerfile`. This allows the entire `BindCraft` environment, including all its dependencies (Python packages, specific versions of `jax`, `jaxlib` with CUDA support, `ColabDesign`, and AlphaFold2 weights), to be encapsulated into a single, runnable container image. This greatly simplifies setup, ensures reproducibility across different environments, and makes the application easier to deploy.
2.  **Streamlined Dependency Management:** Instead of relying on a shell script (`install_bindcraft.sh`) that might have varying behaviors across systems, the `Dockerfile` explicitly lists and installs all necessary dependencies using `conda` and `pip`. This ensures a predictable and consistent installation process within the container.
3.  **Pre-configured Environment:** The Docker image pre-configures the working directory, copies essential application files (`bindcraft.py`, `functions/`, `settings_target/`, etc.), and even downloads and extracts AlphaFold2 model weights during the image build process. This means a user can simply run the Docker container and have a fully functional `BindCraft` instance ready to use, without manual post-installation steps.

### Significant New Features or Improvements:

*   **One-command Deployment:** The Docker image simplifies the deployment of `BindCraft` from a multi-step manual installation to a single `docker run` command (after building the image).
*   **Version Pinning for Dependencies:** By specifying exact versions or ranges for many Python packages within the `conda install` command, the Dockerfile helps prevent "dependency hell" and ensures the application runs with tested configurations.
*   **CUDA Integration:** The Dockerfile explicitly handles CUDA-enabled `jaxlib` and `cuda-nvcc` installation, indicating an intent to support GPU acceleration out-of-the-box within the container, which is crucial for computational tasks like those likely performed by `BindCraft`.
*   **Automated AlphaFold2 Weight Download:** The inclusion of logic to download and extract AlphaFold2 weights directly in the Docker build process is a major convenience, eliminating a common manual setup step.

### Notable Code Refactoring or Architectural Changes:

*   **Shift from Script-based Installation to Containerization:** This is a fundamental architectural shift. The `install_bindcraft.sh` script is now largely superseded by the `Dockerfile`'s build process.
*   **Explicit Pathing and Permissions:** The Dockerfile explicitly sets `WORKDIR /app` and copies files relative to it, and also sets execute permissions for `dssp` and `DAlphaBall.gcc`, ensuring these executables function correctly within the container.
*   **Configuration Adaptations:** The `Configs adapted for Docker` commit suggests minor adjustments were made to existing configuration files (`functions/DAlphaBall.gcc`, `functions/dssp`, `settings_target/PDL1_new.json`) to better suit the containerized environment, although the specific changes are not detailed in the provided diff for those files.

### Potential Impact or Value of the Changes:

*   **Increased Accessibility:** Lowering the barrier to entry for new users or developers who want to try or contribute to `BindCraft`.
*   **Enhanced Reproducibility:** Ensuring that experiments and analyses conducted with `BindCraft` can be reliably reproduced by others, which is critical in scientific computing.
*   **Simplified Production Deployment:** Makes it easier to deploy `BindCraft` in cloud environments or on different servers without extensive setup.
*   **Reduced Support Overhead:** Fewer issues related to environment setup and dependency conflicts.

### Tags:

*   installation
*   feature
*   improvement
*   refactor

**Commits:**

- [3c616d0e](/commit/3c616d0ef13f322f2f9aecbfe29c59664c2351ed) - <span style="color:green">+66</span>/<span style="color:red">-2</span> (2 files): update Dockerfile [Lorenzo Gatti <lorenzo.gatti.89@gmail.com>]

- [f3aae7a4](/commit/f3aae7a43446bb407ede4f81aad8975a3bf7a2df) - <span style="color:green">+16</span>/<span style="color:red">-1</span> (5 files): Configs adapted for Docker [Lorenzo Gatti <lorenzo.gatti.89@gmail.com>]


---

### [LevitateBio/BindCraft](https://github.com/LevitateBio/BindCraft)

**Stats:**
- Commits ahead: 2
- Commits behind: 19
- Stars: 0

- Pull Requests:


- Last updated: 2025-02-07T18:56:57+00:00

**Summary of Changes:**
This fork introduces changes primarily focused on simplifying the build and deployment process.

**Main Themes and Purpose:**
The main purpose of these changes is to containerize the application and automate its build process using Drone CI. This will streamline development, testing, and deployment by providing a consistent and reproducible environment.

**Significant New Features or Improvements:**
*   **Docker Integration:** The addition of a `Dockerfile` allows the application to be easily built into a Docker image, making it portable and runnable across various environments without worrying about dependency conflicts.
*   **Automated CI/CD with Drone:** The `.drone.yml` file configures Drone CI to automatically build the Docker image. This sets up a continuous integration pipeline, ensuring that every code change is automatically built and potentially tested.

**Notable Code Refactoring or Architectural Changes:**
*   There are no significant code refactoring or architectural changes to the application's core logic itself. The changes are external to the application, focusing on its build and deployment infrastructure.

**Potential Impact or Value:**
These changes significantly improve the project's operational efficiency. Developers will benefit from a consistent development environment, faster onboarding, and automated builds. It also lays the groundwork for future continuous deployment strategies.

**Tags:**
*   installation
*   ci

**Commits:**

- [3a348a1a](/commit/3a348a1a5e0cb2af426de63df5053d39d81b369b) - <span style="color:green">+0</span>/<span style="color:red">-0</span> (0 files): drone build [Brandon Frenz <brandon.frenz@gmail.com>]

- [6b254e21](/commit/6b254e21e0801c8174e42ff59e614cbe948dbaac) - <span style="color:green">+94</span>/<span style="color:red">-0</span> (3 files): added docker and drone files [Brandon Frenz <brandon.frenz@gmail.com>]


---

### [coreyhowe999/BindCraft](https://github.com/coreyhowe999/BindCraft)

**Stats:**
- Commits ahead: 2
- Commits behind: 44
- Stars: 0

- Pull Requests:


- Last updated: 2024-10-22T17:15:04+00:00

**Summary of Changes:**
The recent changes primarily focus on refining the installation process for BindCraft, making it more robust and user-friendly.

**Main Themes and Innovations:**

*   **Improved Installation Robustness:** The installer now includes checks to ensure that AlphaFold2 parameters are only downloaded if they are not already present, preventing redundant downloads and potential issues.
*   **Streamlined Conda Environment Management:** The script now activates the created "BindCraft" conda environment directly after creation, rather than relying on a separate activation step. This simplifies the installation flow.
*   **Error Handling and User Feedback:** Enhanced error messages and clearer prompts are introduced throughout the script, providing better feedback to the user during the installation process.
*   **Reduced Verbosity:** The `echo -e` commands have been replaced with `echo` or `printf` for more consistent output, and some redundant checks have been removed.

**Significant New Features or Improvements:**

*   **Conditional AlphaFold2 Parameter Download:** The installer now checks for the existence of the `params` directory before attempting to download AlphaFold2 weights. This is a significant improvement for re-runs or installations where these files might already be present.
*   **Simplified Conda Activation:** The `source` command is now used directly with the path to the `BindCraft` environment, making the activation more direct and less prone to issues with `conda activate`.

**Notable Code Refactoring or Architectural Changes:**

*   **Removal of Redundant Checks:** Several checks for conda environment existence and package installation verification have been removed, streamlining the script. While these checks can be useful for debugging, their removal simplifies the script for a standard successful installation path.
*   **Consolidation of Print Statements:** The use of `echo -e` has been largely replaced by `echo` or `printf`, which is a minor stylistic and consistency improvement.

**Potential Impact or Value:**

These changes will significantly improve the user experience for installing BindCraft by making the process more resilient to interruptions, reducing unnecessary downloads, and providing clearer feedback. The more direct handling of conda environments should also lead to fewer installation-related issues.

**Tags:**
*   installation
*   improvement
*   refactor

**Commits:**

- [5dca3a88](/commit/5dca3a88fb5d5d166e7fafb5179b1e61bdf59cfc) - <span style="color:green">+5</span>/<span style="color:red">-5</span> (1 files): Update install_bindcraft.sh [coreyhowe9 <37548364+coreyhowe999@users.noreply.github.com>]

- [89051f91](/commit/89051f91559442740d6998e319080530db2c2787) - <span style="color:green">+14</span>/<span style="color:red">-9</span> (1 files): Update install_bindcraft.sh [coreyhowe9 <37548364+coreyhowe999@users.noreply.github.com>]


---

### [oceanefollonier/BindCraft](https://github.com/oceanefollonier/BindCraft)

**Stats:**
- Commits ahead: 1
- Commits behind: 0
- Stars: 0

- Pull Requests:


- Last updated: 2025-07-02T14:01:23+00:00

**Summary of Changes:**
The provided diff shows a single commit in a fork of a repository.

### Summary of Changes:

This commit primarily focuses on **removing existing files and adding a minimal `.gitignore` file**. The drastic reduction in lines of code (958 deletions vs. 44 insertions) suggests a significant cleanup or a re-scoping of the project.

**Main Themes:**
*   **Project Scoping/Cleanup:** The large number of deletions, particularly of configuration and installation scripts, indicates a move towards a more streamlined or specific purpose for this fork, potentially removing components not immediately relevant to the current user's needs.
*   **Environment Configuration:** The introduction of a `.gitignore` file points to a focus on managing project-specific temporary files and logs.

**Significant New Features or Improvements:**
*   **None apparent.** The changes are predominantly removals and basic configuration.

**Notable Code Refactoring or Architectural Changes:**
*   **Removal of Installation Script:** `install_bindcraft.sh` has been removed, suggesting a change in how the project is intended to be set up or that setup is now handled externally/manually.
*   **Removal of SLURM Script:** `bindcraft.slurm` removal implies that the SLURM cluster integration, if it existed, is no longer part of this specific fork's scope or is managed differently.
*   **Removal of Example Data/Configuration:** The removal of `example/PDL1.pdb` and `settings_target/PDL1.json` indicates that the specific example or target configuration is either no longer needed, will be provided separately, or is being generalized.

**Potential Impact or Value of the Changes:**
*   **Reduced Project Footprint:** The changes significantly reduce the repository's size and complexity by removing apparently unused or irrelevant files.
*   **Streamlined Focus:** This fork might be tailored for a very specific use case, discarding general-purpose components.
*   **Potential for External Dependencies:** The removal of local installation scripts might mean that the project now relies on external tools or pre-existing environments for its setup.

### Tags:
*   `refactor`
*   `installation` (due to removal of install script)
*   `documentation` (implied by removal of example/config files, making the project less self-describing)

**Commits:**

- [460dfe3f](/commit/460dfe3f057dc9b2ee73eed8bd2eeaa2b833e873) - <span style="color:green">+44</span>/<span style="color:red">-958</span> (5 files): changes to run original [oceane.follonier <oceane.follonier@unibas.ch>]


---

### [kimdn/BindCraft](https://github.com/kimdn/BindCraft)

**Stats:**
- Commits ahead: 1
- Commits behind: 30
- Stars: 0

- Pull Requests:


- Last updated: 2025-05-15T06:41:19+00:00

**Summary of Changes:**
The user is asking for a summary of changes in a GitHub fork. The provided information is a single commit.

Here's an analysis of the commit and the summary:

**Analysis of the Commit:**

The commit `[2187ac7c](https://github.com/martinpacesa/BindCraft/commit/2187ac7c)` titled "Created using Colab" by Doo Nam Kim primarily modifies the `notebooks/BindCraft.ipynb` Jupyter Notebook.

Key changes observed from the diff:

*   **Addition of a Colab Badge:** A new markdown cell is added at the very beginning of the notebook with a "Open In Colab" badge, linking to the fork's specific path on GitHub. This is a common practice for Colab notebooks to allow users to easily open and run them in Google Colab.
*   **Minor change in `prediction_protocol_tag` logic:** In the "Advanced settings" section, the original code had `prediction_protocol_tag` always include the `prediction_protocol_tag` in the `advanced_settings_path` string. The new code introduces a conditional: `if design_protocol in ["Peptide"]:` then `prediction_protocol_tag` is an empty string, otherwise it follows the previous logic. This suggests a refinement in how advanced settings JSON files are named or selected based on the chosen design protocol, specifically for peptide designs.
*   **Change in `trajectory_metrics` extraction:** The line `trajectory_metrics = copy_dict(trajectory._tmp["best"]["aux"]["log"])` is changed to `trajectory_metrics = copy_dict(trajectory.aux["log"])`. This indicates a simplification or correction in how the logging metrics from the `trajectory` object are accessed. It suggests that the `_tmp["best"]` intermediate step might be redundant or incorrect in the context of the updated ColabDesign library or internal BindCraft logic.
*   **Minor change in Colab metadata:** The `gpuType` in the notebook's metadata changed from "A100" to "T4". This is an environmental change, likely reflecting the default or preferred GPU type in Google Colab for this user.

**Summary of Changes:**

This commit primarily updates the `BindCraft.ipynb` Google Colab notebook. The main theme of the changes is to improve the user experience and potentially address compatibility with the underlying libraries in a Colab environment.

**New Features/Improvements:**

*   **Improved Colab Integration:** The addition of the "Open In Colab" badge makes it easier for users to launch and interact with the BindCraft pipeline directly from GitHub in Google Colab.
*   **Refined Advanced Settings Logic:** The conditional handling of `prediction_protocol_tag` for "Peptide" design protocols suggests a more precise control over the advanced settings configurations, potentially leading to more appropriate model selection or naming conventions for specific design tasks.
*   **Code Simplification/Correction:** The change in accessing `trajectory_metrics` likely simplifies the code or corrects an access path, which can lead to more robust execution.

**Notable Code Refactoring/Architectural Changes:**

*   The change in `trajectory_metrics` access could imply a minor internal API change or clarification within the `ColabDesign` library or BindCraft's wrappers around it, leading to a more direct way of retrieving logged data.
*   The conditional logic for `prediction_protocol_tag` is a small refactoring to ensure correct advanced settings path generation based on design protocol type.

**Potential Impact/Value:**

The changes improve the usability of BindCraft for users running it in Google Colab by providing a direct launch link and potentially fixing or refining how certain advanced settings are applied. The correction in `trajectory_metrics` access ensures that performance metrics are correctly extracted. Overall, these are quality-of-life improvements for Colab users and minor bug fixes/refinements for the application's logic.

**Tags:**

*   "ui"
*   "functionality"
*   "refactor"
*   "bugfix" (for the `trajectory_metrics` access, assuming it was an issue)

**Commits:**

- [2187ac7c](/commit/2187ac7cf02366f41b5e9dbba8df39f088ecf39e) - <span style="color:green">+56</span>/<span style="color:red">-11</span> (1 files): Created using Colab [Doo Nam Kim <doonam.kim@gmail.com>]


---

### [Mnemeth101/BindCraft](https://github.com/Mnemeth101/BindCraft)

**Stats:**
- Commits ahead: 1
- Commits behind: 13
- Stars: 0

- Pull Requests:

  - [PR #1](https://github.com/martinpacesa/BindCraft/pull/241)


- Last updated: 2025-05-14T17:45:34+00:00

**Summary of Changes:**
This commit updates the `BindCraft.ipynb` notebook to correctly use the `prediction_protocol` output.

**Summary of Changes:**

The primary purpose of this change is to fix an issue in the `BindCraft.ipynb` Jupyter notebook where the code was attempting to access prediction metrics from an incorrect internal structure of the `trajectory` object. Previously, it was trying to access `trajectory._tmp["best"]["aux"]["log"]`, which is not the correct way to retrieve the auxiliary log data. The fix changes this to `trajectory.aux["log"]`, which is the intended access path for the prediction metrics.

Additionally, a subsequent conditional check for `trajectory.aux["log"]["terminate"]` was also updated to use the already extracted `trajectory_metrics` dictionary, becoming `trajectory_metrics['terminate']`. This improves code readability and consistency.

**Main Themes:**
* Bug fixing in notebook execution logic.

**Significant New Features or Improvements:**
* No new features are introduced. The change improves the reliability of an existing workflow within the notebook.

**Notable Code Refactoring or Architectural Changes:**
* This is a minor refactoring of data access within the notebook, aligning it with the expected structure of the `trajectory` object.

**Potential Impact or Value:**
This fix ensures that the `BindCraft.ipynb` notebook correctly extracts and utilizes prediction metrics (such as plddt, ptm, pae) and termination signals, allowing the downstream steps of the binder hallucination and relaxation process to function as intended. Without this fix, the notebook might fail to process results correctly or might misinterpret the prediction outcomes.

**Tags:**
* functionality
* bugfix

**Commits:**

- [f9205fc4](/commit/f9205fc44f81c7d1fc41b8df9a762b1a0c629e54) - <span style="color:green">+1</span>/<span style="color:red">-1</span> (1 files): Update BindCraft.ipynb to actually use prediction_protocol [Mnemeth101 <31319544+Mnemeth101@users.noreply.github.com>]


---

### [LeeGwangbae/BindCraft](https://github.com/LeeGwangbae/BindCraft)

**Stats:**
- Commits ahead: 1
- Commits behind: 15
- Stars: 0

- Pull Requests:


- Last updated: 2025-04-03T13:28:33+00:00

**Summary of Changes:**
This commit introduces a minor but significant fix to the `install_bindcraft.sh` script, which is responsible for setting up the BindCraft environment.

### Summary of Changes:

The core change is the modification of the path used to activate the Conda environment. Previously, the script attempted to activate the environment using `source ${CONDA_BASE}/bin/activate`. This has been corrected to `source ${CONDA_BASE}/Scripts/activate`. This change suggests an adaptation for environments where Conda activation scripts are located in a `Scripts` directory (common in Windows Conda installations) rather than `bin` (common in Linux/macOS).

Additionally, a trailing newline character was added at the end of the script, which is a common practice for shell scripts to ensure proper execution and avoid potential issues with some parsers or editors.

### Main Themes and Innovations:

*   **Improved Cross-Platform Compatibility (Conda Activation):** The primary innovation is the adjustment to the Conda environment activation path, which likely resolves installation issues for users on specific operating systems (e.g., Windows) where Conda's activation scripts reside in `Scripts` rather than `bin`. This makes the installation process more robust across different environments.

### Tags:

*   installation
*   bugfix
*   functionality

**Commits:**

- [48bc61de](/commit/48bc61dead4081aaf151016000c50cb41db6853a) - <span style="color:green">+2</span>/<span style="color:red">-2</span> (1 files): Update install_bindcraft.sh [LeeGwangbae <bae31728241@gmail.com>]


---

### [YaoYinYing/BindCraft](https://github.com/YaoYinYing/BindCraft)

**Stats:**
- Commits ahead: 1
- Commits behind: 15
- Stars: 0

- Pull Requests:


- Last updated: 2025-03-24T04:29:35+00:00

**Summary of Changes:**
This commit addresses a minor issue in the `install_bindcraft.sh` script, specifically related to how the Conda environment path is determined and used during activation.

**Summary of Changes:**

The primary change is in how the `BindCraft` Conda environment directory is identified. Previously, the script assumed the environment would always be located at `${CONDA_BASE}/envs/BindCraft`. This commit modifies the script to dynamically retrieve the correct environment path using `conda info -e | grep BindCraft | awk '{print $2}'`. This makes the installation script more robust by not relying on a fixed path, which can vary depending on the Conda installation or user configuration. The activation command and subsequent informational messages are updated to use this newly retrieved `CONDA_ENV_DIR` variable.

**Main Themes/Purposes:**

*   **Robustness:** Improves the reliability of the installation script by correctly identifying the Conda environment path dynamically.

**Significant New Features or Improvements:**

*   **Dynamic Conda Environment Path Resolution:** The script now dynamically determines the Conda environment's installation directory, making it more resilient to varying Conda setups.

**Notable Code Refactoring or Architectural Changes:**

*   Introduction of `CONDA_ENV_DIR` variable to store the dynamically retrieved Conda environment path.

**Potential Impact or Value:**

This change primarily benefits users with non-standard Conda installations or those where the default environment location is not used. It prevents potential activation failures during the installation process, leading to a smoother user experience.

**Tags:**

*   functionality
*   bugfix
*   improvement
*   installation

**Commits:**

- [d2e595d9](/commit/d2e595d9e9fbf1af241fb6bed78574b25f6d2d61) - <span style="color:green">+4</span>/<span style="color:red">-3</span> (1 files): fix install script:conda-env-dir [YaoYinYing <33014714+YaoYinYing@users.noreply.github.com>]


---

### [germanne/BindCraft](https://github.com/germanne/BindCraft)

**Stats:**
- Commits ahead: 1
- Commits behind: 19
- Stars: 0

- Pull Requests:

  - [PR #1](https://github.com/martinpacesa/BindCraft/pull/162)


- Last updated: 2025-01-31T07:44:44+00:00

**Summary of Changes:**
This commit introduces a new `environment.yml` file, defining a Conda environment named "BindCraft".

**Summary of Changes:**

The primary purpose of this change is to streamline the installation and management of dependencies for the project. By providing a `conda` environment file, users can easily set up a consistent and reproducible development or execution environment.

**Key Innovations/Improvements:**

*   **Simplified Dependency Management:** This file centralizes all required Python packages and their versions, making it much easier for new users to get started without manually installing each dependency.
*   **Reproducible Environments:** Conda environments ensure that the exact versions of libraries used for development are replicated, reducing "it works on my machine" issues.
*   **CUDA/GPU Support:** The inclusion of `nvidia` and `cuda-nvcc`, `cudnn` channels and specific `jax` packages (e.g., `jax[cuda12]`, `jax-cuda12-pjrt`) indicates a strong focus on enabling GPU-accelerated computations, likely for machine learning or scientific computing tasks.
*   **Specific Libraries:** The environment includes a mix of common scientific computing libraries (pandas, matplotlib, numpy, scipy, biopython), visualization tools (seaborn, py3dmol, ffmpeg), and machine learning frameworks (flax, dm-haiku, chex, optax, colabdesign, jax). The `pyrosetta` dependency suggests a bioinformatics or structural biology focus.

**Potential Impact or Value:**

This change significantly improves the project's accessibility and usability for developers and researchers. It reduces setup friction, ensures environment consistency, and explicitly supports GPU acceleration, which is crucial for performance in many scientific and ML applications. The combination of libraries points towards a project dealing with computational biology, protein design, or similar fields.

**Tags:**
installation, functionality, improvement

**Commits:**

- [dd4a6da6](/commit/dd4a6da6a904aa7022a11efb71a7ca747632bcf4) - <span style="color:green">+37</span>/<span style="color:red">-0</span> (1 files): ADD: conda environment.yml [germann_e <elsa.germann@psi.ch>]


---

### [jinyisd/BindCraft](https://github.com/jinyisd/BindCraft)

**Stats:**
- Commits ahead: 1
- Commits behind: 19
- Stars: 0

- Pull Requests:


- Last updated: 2025-01-10T09:47:54+00:00

**Summary of Changes:**
This commit introduces a minor but important fix to the `install_bindcraft.sh` script, which is responsible for setting up the BindCraft environment.

**Main Theme:** Installation robustness and compatibility.

**New Features/Improvements:**
- The primary change is the addition of the `--no-same-owner` flag to the `tar` command used for extracting AlphaFold2 weights. This flag prevents `tar` from attempting to restore the original owner and permissions of the extracted files.

**Potential Impact/Value:**
This change is crucial for environments where the user running the installation script does not have root privileges or where the file system does not support preserving ownership (e.g., certain Docker environments, NFS mounts, or specific user setups). Without this flag, the extraction process could fail if `tar` tries to set an owner that doesn't exist on the system or if it lacks the necessary permissions, leading to a broken installation. By adding `--no-same-owner`, the script becomes more robust and compatible across a wider range of user and system configurations, ensuring a smoother installation experience for BindCraft.

**Tags:**
- "bugfix"
- "installation"
- "improvement"

**Commits:**

- [ea5cdefa](/commit/ea5cdefa6fb3d7e44a501133f0fdb27f476a166c) - <span style="color:green">+2</span>/<span style="color:red">-2</span> (1 files): Update install_bindcraft.sh [jinyisd <jinyi2023@shanghaitech.edu.cn>]


---

### [Poko18/BindCraft](https://github.com/Poko18/BindCraft)

**Stats:**
- Commits ahead: 1
- Commits behind: 19
- Stars: 0

- Pull Requests:


- Last updated: 2025-01-04T09:15:01+00:00

**Summary of Changes:**
This commit introduces minor changes across several files, primarily focusing on general improvements and possibly some setup.

**Summary of Changes:**

The changes are small in scope, primarily consisting of minor adjustments to existing files and the addition of a standard Python `.gitignore` file. The modifications in `bindcraft.py` and `colabdesign_utils.py` suggest minor refinements to core functionalities, potentially related to data handling or utility functions. The changes in the `settings_advanced` JSON files indicate subtle tweaks to configuration parameters, likely for different multi-mer modeling stages, possibly improving flexibility or performance.

**Main Themes and Purpose:**

*   **Code Cleanup and Best Practices:** The addition of `.gitignore` indicates a move towards better repository hygiene.
*   **Minor Configuration Refinement:** Adjustments to advanced settings files suggest fine-tuning of existing models or workflows.
*   **Subtle Code Adjustments:** Small changes in Python scripts imply ongoing development and minor improvements.

**Significant New Features or Improvements:**

No significant new features are introduced. The changes are more about iterative improvements and maintenance.

**Notable Code Refactoring or Architectural Changes:**

No major refactoring or architectural changes are apparent from this single commit.

**Potential Impact or Value:**

The impact is likely minimal but positive. The `.gitignore` addition is a standard practice that helps keep the repository clean. The small adjustments to Python scripts and configuration files likely contribute to stability, minor performance gains, or increased flexibility in specific multi-mer modeling scenarios.

**Tags:**
*   improvement
*   refactor

**Commits:**

- [b2017dfc](/commit/b2017dfc5192c68fb649ac9e9aa29a7022648c1c) - <span style="color:green">+23</span>/<span style="color:red">-18</span> (9 files): minor changes [Poko18 <tadej.satler@gmail.com>]


---

### [ChanceChallacombe/BindCraft](https://github.com/ChanceChallacombe/BindCraft)

**Stats:**
- Commits ahead: 1
- Commits behind: 38
- Stars: 0

- Pull Requests:


- Last updated: 2024-10-31T23:18:48+00:00

**Summary of Changes:**
This commit introduces significant enhancements to the `binder_hallucination` function within `colabdesign_utils.py`, primarily focusing on providing more flexible and advanced options for binder design.

The main themes of these changes are:
1.  **Increased Control over Binder Design:** New parameters allow for more granular control over how the binder is prepared and designed, including the ability to specify an existing binder chain, fixed positions, and loops.
2.  **Improved Robustness and Efficiency:** Minor adjustments to the design process, such as clearing the best model before PSSM semigreedy optimization and increasing the minimum contact threshold, aim to improve the quality and relevance of designed binders.
3.  **Enhanced MPNN Integration:** The MPNN sequence generation process is updated to leverage parallel sampling, potentially speeding up sequence generation.

**Significant New Features or Improvements:**
*   The `binder_hallucination` function now accepts `binder_chain`, `pos`, and `loops` parameters. This allows users to:
    *   Initiate design with an existing binder chain (`binder_chain`).
    *   Specify exact positions and lengths for the binder (`pos`, `length`).
    *   Define loops within the binder for more structured design (`loops`), which can be rewired.
*   The `af_model.prep_inputs` call within `binder_hallucination` is now conditional based on these new parameters, enabling different input preparation strategies.
*   `af_model.clear_best()` is called before `design_pssm_semigreedy` optimization, which can prevent the optimizer from being stuck with a suboptimal "best" model from previous stages.
*   The minimum number of interface contacts required for a binder to be considered valid has been increased from 3 to 7. This change aims to filter out binders with poor or insufficient interaction with the target, leading to more meaningful designs.
*   The `mpnn_gen_sequence` function now uses `mpnn_model.sample_parallel` instead of `mpnn_model.sample`, allowing for parallel sampling of MPNN sequences, which can accelerate the design process for multiple sequences.
*   The `predict_binder_complex` function has been renamed to `masked_binder_predict` for clarity.

**Notable Code Refactoring or Architectural Changes:**
*   The signature of the `binder_hallucination` function has been extended to include the new parameters.
*   Conditional logic has been added around `af_model.prep_inputs` to handle the new binder design options.
*   A minor fix was applied to the `fixed_positions` string in `mpnn_gen_sequence` to prevent an unnecessary trailing comma.

**Potential Impact or Value of the Changes:**
These changes significantly enhance the flexibility and power of the binder design pipeline. Users can now perform more targeted and sophisticated binder design, including re-designing existing binders, specifying precise structural constraints, and potentially generating higher-quality designs due to improved filtering and optimization strategies. The parallel MPNN sampling can lead to faster iteration times for sequence generation.

**Tags:**
*   feature
*   functionality
*   improvement
*   refactor

**Commits:**

- [4cbd19b2](/commit/4cbd19b206f62fae03b9a93ae269ab3cbd377986) - <span style="color:green">+15</span>/<span style="color:red">-4</span> (1 files): add options for binder_hallucination [ChanceChallacombe <chance.challacombe@gmail.com>]


---

### [rui-teixeira/BindCraft](https://github.com/rui-teixeira/BindCraft)

**Stats:**
- Commits ahead: 1
- Commits behind: 39
- Stars: 0

- Pull Requests:


- Last updated: 2024-10-26T10:00:20+00:00

**Summary of Changes:**
The provided commit introduces a new Jupyter Notebook, `BindCraft_EGFR_1.ipynb`, to the `notebooks` directory. This notebook appears to be a self-contained pipeline for protein binder design using computational methods, specifically targeting the EGFR protein.

### Main Themes and Purpose:
The primary purpose of this change is to provide a user-friendly, interactive environment (likely Google Colab) for designing protein binders. It streamlines a complex computational workflow, making it accessible for researchers who may not have extensive programming or infrastructure expertise.

### Significant New Features or Improvements:
*   **Complete Binder Design Pipeline:** The notebook integrates multiple computational tools (AlphaFold2, MPNN, PyRosetta) into a single, executable workflow for de novo protein binder design.
*   **Google Colab Integration:** The notebook is designed to run on Google Colab, leveraging its free GPU resources (A100 specified in metadata). This includes:
    *   Automated installation of dependencies (ColabDesign, PyRosetta, AlphaFold parameters) from GitHub and Google Cloud Storage.
    *   Google Drive mounting for persistent storage of design results, allowing users to resume interrupted sessions.
*   **Configurable Design Parameters:** Users can easily set key design parameters through interactive Colab forms, such as:
    *   Target PDB file and chains
    *   Target hotspot residues
    *   Binder length range
    *   Number of desired final designs
    *   Advanced design protocols ("Default", "Beta-sheet", "Peptide")
    *   Filtering options ("Default", "Peptide", "None")
*   **Automated Design and Validation Loop:** The core of the notebook is a loop that:
    *   Hallucinates initial binder designs using AlphaFold2 backpropagation.
    *   Performs sequence redesign using MPNN.
    *   Predicts complex structures with AlphaFold2.
    *   Calculates various biophysical metrics (clashes, interface scores, secondary structure content, RMSD).
    *   Applies user-defined filters to accept or reject designs.
    *   Saves accepted designs and statistics, and tracks rejected designs and reasons.
*   **Results Management and Visualization:**
    *   Organized output directory structure for designs, relaxed structures, animations, and plots.
    *   Generation of CSV files (`trajectory_stats.csv`, `mpnn_design_stats.csv`, `final_design_stats.csv`, `failure_csv.csv`) to track the progress and metrics of all generated designs.
    *   Automated ranking of accepted designs based on `Average_i_pTM` (predicted TM-score for interface).
    *   Visualization of the top design using Py3Dmol and display of design animations.
*   **Robustness:** Includes checks for GPU availability, existing installations, and handles duplicate sequences.

### Notable Code Refactoring or Architectural Changes:
*   **Modular Functions:** The notebook heavily relies on external Python functions imported from `bindcraft.functions`. This suggests a well-structured backend for the computational steps, keeping the notebook clean and focused on workflow orchestration and user interaction.
*   **JSON-based Configuration:** Design settings, advanced options, and filters are stored and loaded from JSON files, facilitating easy modification and sharing of configurations.
*   **Extensive Metric Collection:** The pipeline collects a large array of metrics at different stages (hallucination, MPNN redesign, complex prediction) to provide comprehensive insights into design quality and aid in filtering.

### Potential Impact or Value:
This notebook significantly lowers the barrier to entry for performing complex protein binder design. It enables researchers without specialized computational resources or deep bioinformatics knowledge to leverage state-of-the-art AI-driven protein design methods. Its direct integration with Google Colab and Google Drive makes it highly accessible and practical for iterative design cycles, potentially accelerating drug discovery and protein engineering efforts.

### Tags:
*   feature
*   installation
*   functionality
*   ui
*   documentation
*   refactor

**Commits:**

- [6db6be18](/commit/6db6be183e22a184828ecd3b9a5a1a6169f24484) - <span style="color:green">+910</span>/<span style="color:red">-0</span> (1 files): Created using Colab [Rui Teixeira <rui.teixeira.eng@gmail.com>]


---

### [Goosang-Yu/BindCraft](https://github.com/Goosang-Yu/BindCraft)

**Stats:**
- Commits ahead: 1
- Commits behind: 56
- Stars: 0

- Pull Requests:


- Last updated: 2024-10-02T16:09:18+00:00

**Summary of Changes:**
This commit introduces the initial scaffolding for a new Python project named `bindcraft`.

**Main Themes and Purpose:**

The primary purpose of these changes is to establish the basic structure and metadata for a Python package. It sets up the project for future development and distribution.

**Significant New Features or Improvements:**

*   **Project Initialization:** Creates the `bindcraft` package structure.
*   **Version Management:** Defines the initial version `0.1.0` in `__init__.py`.
*   **Build System Configuration:** Configures `pyproject.toml` to use `hatch` for building the project, indicating a modern approach to packaging.
*   **Utility Module:** Starts a `bindcraft.utils` subpackage with a `functional.py` module, suggesting an intent to include reusable utility functions.

**Notable Code Refactoring or Architectural Changes:**

This is an initial commit, so there's no refactoring of existing code. However, it establishes a clear architectural pattern for a Python package, separating core functionality from utilities.

**Potential Impact or Value:**

This commit lays the groundwork for a new Python project. It enables future development, dependency management, and eventual distribution of the `bindcraft` package. The use of `hatch` suggests a focus on modern, efficient packaging.

---

**Tags:**

*   `installation`
*   `feature`

**Commits:**

- [e40a08b0](/commit/e40a08b0365556d11e3f62993b57742589e96e5c) - <span style="color:green">+78</span>/<span style="color:red">-0</span> (4 files): ✨ [Goosang Yu <gsyu93@gmail.com>]


---



## Summary of Most Interesting Forks

The analysis of the BindCraft forks reveals a vibrant development ecosystem, with significant efforts focused on improving usability, extending design capabilities, and enhancing deployment.

The most impactful forks are **alpha29/BindCraft_mess**, **SuperChrisW/BindCraft**, **WBennett003/BindCraft_SharpLab**, and **lindseyguan/BindCraft**. Alpha29/BindCraft_mess stands out for its comprehensive refactoring into a structured Python package, modern dependency management with Poetry, and the development of a user-friendly command-line interface, which dramatically improves maintainability and accessibility. SuperChrisW/BindCraft introduces critical advancements in protein design by integrating MPNN and FastRelax protocols, promising higher-quality designs and more efficient screening. WBennett003/BindCraft_SharpLab pushes customization further with its "custom pipeline" functionality, allowing users to define intricate multi-stage design workflows and integrate diverse external tools like Fampnn and DiffDock-PP, making BindCraft highly versatile for complex research. Finally, lindseyguan/BindCraft brings a powerful new capability: joint optimization against multiple targets, including "negative targets," which is crucial for designing highly specific binders and addressing a key challenge in protein engineering.

Beyond these major feature additions, several forks demonstrate a strong pattern of improving installation and deployment. Forks like **fabianackle/BindCraft**, **czl368/BindCraft**, **A-Yarrow/BindCraft-Cloud**, **gattil/BindCraft**, **LevitateBio/BindCraft**, and **benediktsinger/BindCraft-uv** all focus on streamlining setup through Conda, virtual environments, SLURM integration, or comprehensive Dockerization. This collective effort indicates a clear need within the community for easier access and more robust environments, especially for computationally intensive tasks in cloud or HPC settings. Another recurring theme is the refinement of Google Colab integration, seen in forks like **eesb99/BindCraft** and **rui-teixeira/BindCraft**, which enhance stability, user experience, and provide interactive, accessible pipelines for protein design.
 