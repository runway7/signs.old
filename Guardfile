
guard 'shell' do
  nose = `which nosetests`.rstrip  
  watch(/(.*).py/) do |m| 
    `bin/python #{nose} --with-snort`    
    `pep8 #{m}`        
  end
end