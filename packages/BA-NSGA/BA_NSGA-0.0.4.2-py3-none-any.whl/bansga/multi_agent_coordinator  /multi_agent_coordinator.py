def run(self, debug=False):
    
    supecell = np.array([1,1,1])
    self.load_partitions(self.dataset_path, self.template_path)
    self.partitions['supercell'] = {}
    for S_i, S in enumerate(self.supercell_steps):

        supecell *= S
        supecell_name = 'supecell_' + '_'.join(map(str, supecell))

        for container in self.partitions['dataset'].containers:
            container.AtomPositionManager.generate_supercell(repeat=S)

        for container in self.partitions['template'].containers:
            container.AtomPositionManager.generate_supercell(repeat=S)

        t0 = time.time()
        self.export_structures(self.partitions['dataset'], f'{self.output_path}/{supecell_name}/generation/initial')
        self.export_structures(self.partitions['dataset'], f'{self.output_path}/{supecell_name}/generation/template')
        self.time_log.setdefault('export_structures', []).append(time.time() - t0)

        partition = self.run_workflow(
                partition=self.partitions['dataset'], 
                template=self.partitions['template'], 
                partition_path=supecell_name, 
                supercell_repeat=list(supecell),
                debug=True)
        self.partitions['supercell'][supecell_name] = partition
        