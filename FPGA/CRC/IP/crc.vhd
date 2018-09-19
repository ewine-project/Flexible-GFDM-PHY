library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.ALL;


library ieee;
library work;
use ieee.std_logic_1164.all;
use ieee.numeric_std.ALL;

-- nc: the length of CRC
-- nd: the length of parallel bits
entity crc is
generic (nd: integer := 8; nc : integer :=16);
    port (
        clk     :in  std_logic;
        reset   :in  std_logic;
		enable   :in  std_logic;
        dataserpulse    :in  std_logic;
        data_i :in  std_logic_vector ((nd-1) downto 0);
        poly : in std_logic_vector((nc-1) downto 0);
        crc_out :out std_logic_vector ((nc-1) downto 0)
    );
end crc;

architecture rtl of crc is
-- compute CRC 
function crc_compute( data_in: in std_logic_vector((nd-1) downto 0);
                g : in std_logic_vector((nc-1) downto 0);             
                     crc_i: in std_logic_vector((nc-1) downto 0))
return std_logic_vector is  
    variable crc_o: std_logic_vector((nc-1) downto 0);
    variable crc_io: std_logic_vector((nc-1) downto 0);
    variable temp : std_logic;
    --variable exit_loop : integer;
begin
    crc_io := crc_i;
    --exit_loop := nd;
     for i in (nd-1) downto 0 loop
         temp := crc_io(nc-1) xor   data_in(i);
         for j in (nc-1) downto 1 loop
           crc_o(j) := (temp and g(j)) xor crc_io(j-1);
         end loop;   
         crc_o(0) := (temp and g(0));
         crc_io := crc_o;
         --exit_loop := (exit_loop-1) ;               
       end loop; 
    
    return crc_o;
    
end;

signal crc_o:   std_logic_vector ((nc-1) downto 0);  -- ADDED register

begin 
  
 process (clk,reset,enable) begin
        if(enable = '1') then
		  if (reset = '1') then
			  crc_o <= (others=>'0');
		  elsif (clk'event and clk='1') then
			  if (dataserpulse = '1') then
				  crc_o <=  (others=>'0');
			  else
				  crc_o <= crc_compute(data_i, poly, crc_o);
			  end if;
		  end if;
		end if;
  end process;    
  	    crc_out <= crc_o;
end rtl;