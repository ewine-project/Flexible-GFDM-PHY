----------------------------------------------------------------------------------
-- Company: TU-Dresden 
-- Engineer: Ahmad Nimr, Bharath Kumar Singh Muralidhar
-- Create Date: 6/2018
-- Design Name: QAM mapping/demapping 
-- Module Name: qam_map - Behavioral
-- 
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
-- helper functions 
package log is
  function log2(input : integer) return integer;
  function sqrt(inp : integer) return integer;
end log;

package body log is
function log2( input:integer ) return integer is
variable temp,log:integer;
begin
  temp:=input;
  log:=0;
  while (temp /= 1) loop
   temp:=temp/2;
   log:=log+1;
   end loop;
   return log;
  end function log2;

  function sqrt(inp : integer) return integer is
    variable count : integer;
    variable res : integer;
begin
    count := log2(inp);
    count := count/2;
    res := 2 ** count;
    return res;
end function sqrt;

end log;

library IEEE;
library work;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use IEEE.STD_LOGIC_SIGNED.ALL;
use work.log.all;

entity qamdemap is
generic (n : integer :=64);
port (clk : in std_logic;
      reset : in std_logic;
      enable : in std_logic;
      i_cmp : in std_logic_vector(((log2(n)/2)+16) downto 0);
      q_cmp : in std_logic_vector(((log2(n)/2)+16) downto 0);
      gray_code : in std_logic;
      index : out std_logic_vector((log2(n)-1) downto 0)
      );
end qamdemap;

architecture Behavioral of qamdemap is
-- Binary to Gray mapping 
function btog (bin : in integer)
return std_logic_vector is
    variable gray : std_logic_vector(((log2(n)/2)-1) downto 0);
    variable bin_std : std_logic_vector(((log2(n)/2)-1) downto 0);
 begin
    bin_std := std_logic_vector(to_signed(bin, (log2(n)/2)));
    gray(((log2(n)/2)-1) downto 0) := bin_std(((log2(n)/2)-1) downto 0);
    for j in (((log2(n)-4)/2)) downto 0 loop
        gray(j) := bin_std(j+1) xor bin_std(j);
    end loop;
    return gray;
end;
-- Binary Mapping of fixed point value of precision  [log2(n)/2].16 (16 bits for the fractional part)
-- to nearest PAM integer value 
function mapp( cmp: in std_logic_vector(((log2(n)/2)+16) downto 0);             
                     g_c : in std_logic )
return std_logic_vector is  
    variable idx_std : std_logic_vector(((log2(n)/2)-1) downto 0);
    variable temp : std_logic_vector(((log2(n)/2)+16) downto 0):= (others => '0');
    variable i : integer range 0 to ((sqrt(n))-1);
begin
    temp(((log2(n)/2)+16) downto 16) := std_logic_vector(to_signed(((sqrt(n))-1), ((log2(n)/2)+1)));
	if ( to_integer(signed(temp)) <= to_integer(signed(cmp))) then -- upper value
	i := ((sqrt(n))-1);
	else 
		if (to_integer(signed(cmp)) <= (-to_integer(signed(temp))) ) then -- lower value
		i := 0;
		else -- in range			
			temp(((log2(n)/2)+16) downto 0) := std_logic_vector(unsigned(temp) + unsigned(cmp));
			temp := std_logic_vector(shift_right(unsigned(temp),1));
		-- Extract the integer part 
			i := to_integer(unsigned(temp(((log2(n)/2)+16) downto 16)));
		-- Round the fractional part (>0.5) i.e. the MSB bit of the fractional part is 1
			if(temp(15) = '1') then 
				i := i+1;
			end if;
		end if;
	end if;
	-- Apply Gray mapping if selected	
    if(g_c = '1') then
            idx_std := btog(i); 
    else 
            idx_std := std_logic_vector(to_signed(i, (log2(n)/2)));
    end if;
     return idx_std;      
end;
begin
   
    process (clk,reset,enable) begin
        if(enable = '1') then
            if (reset = '1') then
                index <= (others => '0');
            elsif (clk'event and clk='1') then 
-- Do de mapping per I/Q component 			
-- I --> MSB, Q --> LSB
                index((log2(n)-1) downto (log2(n)/2)) <= mapp(i_cmp(((log2(n)/2)+16) downto 0),gray_code);
                index(((log2(n)-2)/2) downto 0) <= mapp(q_cmp(((log2(n)/2)+16) downto 0),gray_code);
            end if;
        end if;
    end process;  
end Behavioral;