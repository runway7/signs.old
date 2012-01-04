# A sample Guardfile
# More info at https://github.com/guard/guard#readme

guard 'shell' do  
  watch(/(.*).py/) do |m| 
    `forklift py test`    
    `pep8 #{m}`
  end
end